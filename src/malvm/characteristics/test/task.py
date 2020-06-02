from ..abstract_characteristic import Characteristic, LambdaCharacteristic


class TestCharacteristic(Characteristic):
    def __init__(self):
        super().__init__("T001", "Just a simple test characteristic.")
        self.add_sub_characteristic(
            LambdaCharacteristic(
                "H001",
                "This is an example LambdaCharacteristic.",
                "Hello world.",
                lambda x: ("Hello world.", False),
                lambda x: None,
            )
        )

        self.add_sub_characteristic(
            LambdaCharacteristic(
                "H002",
                "This is an another example LambdaCharacteristic.",
                "Hello world 2.",
                lambda x: ("Hello world the second...", True),
                lambda x: None,
            )
        )
