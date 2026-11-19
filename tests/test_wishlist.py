import pytest
from fastapi import status

from db.models import DbProduct


def create_product(db_session, seller_id, name="camera"):
    product = DbProduct(
        product_name=name,
        description="good quality",
        price=100.0,
        quantity=5,
        published=True,
        seller_id=seller_id,
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


# Test 1 - Add a single product to the wishlist
def test_add_product_to_wishlist(authorized_client, db_session, test_user):
    product = create_product(db_session, seller_id=test_user.id)
    response = authorized_client.post(f"/wishlist/{product.id}")
    assert response.status_code == status.HTTP_201_CREATED


# Test 2 - View an empty wishlist
def test_view_empty_wishlist(authorized_client, test_user):
    response = authorized_client.get("/wishlist/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


# Test 3 - Exists check returns False for a product not on the wishlist
def test_exists_check_returns_false(authorized_client, db_session, test_user):
    product = create_product(db_session, seller_id=test_user.id)
    response = authorized_client.get(f"/wishlist/{product.id}/exists")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is False


# Test 4 - Remove a product from the wishlist
def test_remove_product_from_wishlist(authorized_client, db_session, test_user):
    product = create_product(db_session, seller_id=test_user.id)
    add_response = authorized_client.post(f"/wishlist/{product.id}")
    assert add_response.status_code == status.HTTP_201_CREATED

    delete_response = authorized_client.delete(f"/wishlist/{product.id}")
    assert delete_response.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)

    list_response = authorized_client.get("/wishlist/")
    assert list_response.status_code == status.HTTP_200_OK
    assert list_response.json() == []


# Test 5 - Complete wishlist flow
def test_complete_wishlist_flow(authorized_client, db_session, test_user):
    product = create_product(db_session, seller_id=test_user.id)

    add_response = authorized_client.post(f"/wishlist/{product.id}")
    assert add_response.status_code == status.HTTP_201_CREATED

    list_response = authorized_client.get("/wishlist/")
    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.json()) == 1

    exists_response = authorized_client.get(f"/wishlist/{product.id}/exists")
    assert exists_response.status_code == status.HTTP_200_OK
    assert exists_response.json() is True

    delete_response = authorized_client.delete(f"/wishlist/{product.id}")
    assert delete_response.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT)

    exists_response_after = authorized_client.get(f"/wishlist/{product.id}/exists")
    assert exists_response_after.json() is False


# Test 6 - Wishlist with multiple items
def test_wishlist_with_multiple_items(authorized_client, db_session, test_user):
    products = [create_product(db_session, seller_id=test_user.id, name=f"item{i}") for i in range(3)]

    for product in products:
        response = authorized_client.post(f"/wishlist/{product.id}")
        assert response.status_code == status.HTTP_201_CREATED

    list_response = authorized_client.get("/wishlist/")
    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.json()) == 3
