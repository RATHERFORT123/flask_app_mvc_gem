from ..extensions import db
from ..models.category import Category

def get_all_categories():
    return Category.query.order_by(Category.id).all()

def add_category(value, text):
    if Category.query.filter_by(value=value).first():
        return False  # duplicate, handle as needed
    category = Category(value=value, text=text)
    db.session.add(category)
    db.session.commit()
    return True

def update_category(category_id, value, text):
    category = Category.query.get(category_id)
    if category:
        category.value = value
        category.text = text
        db.session.commit()
        return True
    return False

def delete_category(category_id):
    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        return True
    return False


# from ..extensions import db
# from ..models.category import Category

# def add_category(value, text):
#     if Category.query.filter_by(value=value).first():
#         # Optionally skip duplicates or update
#         return
#     category = Category(value=value, text=text)
#     db.session.add(category)
#     db.session.commit()

# def get_all_categories():
#     return Category.query.all()

# def delete_category(category_id):
#     category = Category.query.get(category_id)
#     if category:
#         db.session.delete(category)
#         db.session.commit()
