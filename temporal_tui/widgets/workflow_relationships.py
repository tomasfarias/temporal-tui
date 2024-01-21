import textual.app
import textual.widgets as widgets

from temporal_tui.models import Workflow


class WorkflowRelationships(widgets.Static):
    def __init__(self, id: str, workflow: Workflow) -> None:
        self.parent_id = workflow.parent_id
        super().__init__(id=id)

    def compose(self) -> textual.app.ComposeResult:
        with widgets.Collapsible(title="Relationships"):
            yield widgets.Label("This workflow doesn't have any relationships")
