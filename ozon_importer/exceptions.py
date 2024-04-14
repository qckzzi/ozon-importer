class ProductTypeNotFoundError(Exception):
    def __init__(self, product_name: str) -> None:
        super().__init__(f"Product type not found at '{product_name}'")
