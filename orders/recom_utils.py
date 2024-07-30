# products/recommendation_utils.py

import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
from .models import Product
from orders.models import Order  # Adjust the import based on your actual app structure

def get_user_product_interactions():
    orders = Order.objects.exclude(order_status=Order.CART_STAGE)
    interactions = []

    for order in orders:
        for item in order.added_items.all():
            interactions.append({
                'user_id': order.owner.id,
                'product_id': item.product.id,
                'quantity': item.quantity
            })

    return pd.DataFrame(interactions)

def train_model():
    # Get interactions data
    interactions_df = get_user_product_interactions()

    # Prepare the data for Surprise
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(interactions_df[['user_id', 'product_id', 'quantity']], reader)

    # Train-test split
    trainset, testset = train_test_split(dataset, test_size=0.2)

    # Use SVD algorithm for recommendations
    algo = SVD()
    algo.fit(trainset)

    # Predict and evaluate
    predictions = algo.test(testset)
    accuracy.rmse(predictions)

    return algo, interactions_df

def get_recommendations(user_id, n=5):
    algo, interactions_df = train_model()
    all_items = interactions_df['product_id'].unique()
    
    # Predict ratings for all items for the given user
    predictions = [algo.predict(user_id, item_id) for item_id in all_items]
    
    # Sort predictions by estimated rating
    recommendations = sorted(predictions, key=lambda x: x.est, reverse=True)
    
    # Return top-n recommendations
    return [Product.objects.get(pk=pred.iid) for pred in recommendations[:n]]
