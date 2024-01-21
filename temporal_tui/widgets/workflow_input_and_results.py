import textual.app
import textual.widgets as widgets

from temporal_tui.models import Workflow


class WorkflowInputAndResults(widgets.Static):
    def __init__(self, id: str, workflow: Workflow):
        super().__init__(id=id)

    def compose(self) -> textual.app.ComposeResult:
        with widgets.Collapsible(title="Inputs and Results"):
            yield widgets.DataTable(id="test")
