import vector
from duit import ui
from duit.arguments.Argument import Argument
from duit.model.DataField import DataField
from duit.ui.ContainerHelper import ContainerHelper

from duit_osc.OscEndpoint import OscEndpoint
from duit_osc.OscService import OscService


class Config:
    def __init__(self):
        container_helper = ContainerHelper(self)

        with container_helper.section("User"):
            self.name = DataField("Cat") | ui.Text("Name") | OscEndpoint()
            self.age = DataField(21) | ui.Slider("Age", limit_min=18, limit_max=99) | OscEndpoint()

        with container_helper.section("Application"):
            self.enabled = DataField(True) | ui.Boolean("Enabled") | Argument()
            self.direction = DataField(vector.obj(x=2, y=5)) | OscEndpoint("dir")

            self.run_algorithm = DataField(lambda: print("hello world from algo")) | OscEndpoint()


def main():
    # create initial config
    config = Config()

    # register a custom listener for the enabled flag
    config.enabled.on_changed += lambda e: print(f"Enabled: {e}")

    def on_age(v: int):
        print(f"Age: {v}")
        config.direction.fire()

    config.age.on_changed += on_age

    # start server
    osc_server = OscService()
    osc_server.add_route("/config", config)

    print(osc_server.api_description())

    print("running")
    osc_server.run()


if __name__ == "__main__":
    main()
