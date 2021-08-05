from malvm.characteristics.product_id import ProductID


def test_product_key_length():
    product_id_characteristic = ProductID()
    new_product_id = product_id_characteristic.new_product_id
    blocks = new_product_id.split("-")
    assert len(blocks) == 4
    assert len(blocks[0]) == 5
    assert len(blocks[1]) == 3
    assert len(blocks[2]) == 7
    assert len(blocks[3]) == 5
