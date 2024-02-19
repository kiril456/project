from web_app import app, db
from flask import render_template, url_for, redirect, flash, get_flashed_messages, request, abort
from flask_login import login_required, current_user
from web_app.forms import ItemForm, CommentForm, ChangeProfileForm, DonateForm
from web_app.modules import Item, Comment, User, Transaction
import base64


def errors_form(form):
    # this func is flashed error message in page 
    if form.errors:
        for err_msg in form.errors.values():
            flash(f"Error: {err_msg[0]}", category="danger")


@app.context_processor
def utility_processor():
    def encode_image(img):
        return base64.b64encode(img).decode("UTF-8")
    return dict(encode_image=encode_image)


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home_page():
    items = Item.query.all()
    search_items = []
    
    # Form for get id from card of item
    if request.method == "POST" and ('purchase_item' in request.form):
        item_id = request.form['purchase_item']

        return redirect(url_for('item_page', item_id=item_id))
    
    # Search form for items
    if request.method == "POST" and ('searched' in request.form):
        search_items = Item.query
        search_data = request.form['searched']

        search_items = search_items.filter(Item.description.like("%" + search_data + "%"))
        search_items = search_items.order_by(Item.description).all()
        
    return render_template("pages/index.html", items=items, search_items=search_items)


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart_page():
    if request.method == 'POST':
        item = Item.query.filter_by(id=request.form['sell_item']).first()
        if item:
            transaction = Transaction(cost=item.price, status="sell", 
                                              item_id=item.id, user_id=current_user.id)
            item.sell(current_user)
            transaction.add_transaction()
            
            Transaction.query.filter(Transaction.item_id==item.id or Transaction.status=="buy").delete()
            db.session.commit()
            
            flash("Item was sold successfully", category="success")
            
            return redirect(url_for("home_page"))
        else:
            flash("Sorry, you can't sell this item", category="danger")
    
    if request.method == 'GET':
        transactions = Transaction.query.filter(Transaction.user_id==current_user.id or Transaction.status=="buy").all()
        items = [Item.query.filter_by(id=transaction.item_id).first() for transaction in transactions]
        return render_template("pages/cart.html", items=items, transactions=transactions)


@app.route('/upload', methods=['POST', "GET"])
@login_required
def upload():
    if current_user.status == 1:
        form = ItemForm()
        
        # Form for upload item by admin
        if form.validate_on_submit():
            description = form.description.data
            price = form.price.data
            pic = form.image.data
            
            if not pic:
                return "No pic uploaded", 400
            
            mimetype = pic.mimetype
            
            # Add item in database 
            item = Item(description=description, price=price, image=pic.read(), mimetype=mimetype)
            db.session.add(item)
            db.session.commit()
            
            flash("Successfuly, Items was send in database", category="success")
        
        errors_form(form)
              
        return render_template('admin/upload.html', form=form)
    
    return redirect(url_for('home_page'))


@app.route('/item/id=<int:item_id>', methods=['GET', 'POST'])
@login_required
def item_page(item_id):
    item = Item.query.filter_by(id=item_id).first()
    
    # if item not exists
    if not item:
        abort(404)    
    
    comments = Comment.query.filter_by(item_id=item_id).all()
    comment_form = CommentForm()
    
    # Get data from form for buy item
    if request.method == 'POST' and ('buy_item' in request.form):
        if item:
            if current_user.budget >= item.price:
                # user buy an item
                if item.amount > 0:
                    transaction = Transaction(cost=item.price, status="buy", 
                                              item_id=item.id, user_id=current_user.id)
                    item.buy(current_user)
                    transaction.add_transaction()
                    
                    flash(f"'{item.description}' was bought!", category="success")
                
                    return redirect(url_for('cart_page'))
                else:
                    flash("Sorry, this item is not available for now", category="info")
            else:
                flash("You don't have enough money to buy it!", category="info")
        else:
            flash("Sorry, Something wrong!", category="danger")
    
    # Add comments    
    if comment_form.validate() and comment_form.comment.data:
        comment_text = comment_form.comment.data
        
        comment = Comment(comment_text)
        comment.add_comment(current_user, item_id)
        
        flash("Comment was posted successfully", category="success")
        
        return redirect(url_for('item_page', item_id=item_id))
    
    return render_template('pages/item.html', item=item, comment_form=comment_form, comments=comments)


@app.route('/profile/username=<name>', methods=['GET', 'POST'])
@login_required
def profile_page(name):
    form = ChangeProfileForm()
    
    # Change profile settings
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if not user or current_user.username == user.username:
            comments = Comment.query.filter_by(author=current_user.username).all()
            current_user.change_profile(username, password)
            
            # Check if current user add any comments and then change username of this comments
            if comments:
                for comment in comments:
                    comment.author_comment = current_user.username       
                    db.session.commit()
            
            flash("Profile was changed successfully", category="success")
            
            return redirect(url_for("profile_page", name=current_user.username))
        else: 
            flash("Sorry, but this username exists. Please try again", category="info")
        
    errors_form(form)
             
    return render_template('auth/profile.html', form=form)


@app.route('/donate-money/username=<username>', methods=['GET', 'POST'])
def get_money_page(username):
    form = DonateForm()
    
    if form.validate_on_submit():
        cash = form.cash.data
        password = form.password.data
        
        if current_user.check_password(password):
            current_user.budget += cash
            db.session.commit()
            
            flash("The payment was successfully", category="success")
            
            return redirect(url_for('home_page'))
        else:
            flash("You entered incorect password. Please try again!", category="info")
            
    return render_template("pages/donate.html", form=form)
        