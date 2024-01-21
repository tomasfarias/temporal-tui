import textual
import textual.app
import textual.widgets as widgets

from temporal_tui.models import Workflow
from temporal_tui.service import TemporalService
from temporal_tui.widgets import WorkflowTable, WorkflowView


class TemporalTUI(textual.app.App):
    def __init__(self, *args, **kwargs) -> None:
        self.workflows = {}
        super().__init__(*args, **kwargs)

    def compose(self) -> textual.app.ComposeResult:
        yield widgets.Header()
        yield WorkflowTable(id="workflows")
        yield widgets.Footer()

    def on_mount(self) -> None:
        self.temporal = TemporalService.from_env()

        workflows_table = self.query_one("#workflows", WorkflowTable)
        workflows_table.set_loading(True)

        self.load_workflows(workflows_table)

    @textual.work
    async def load_workflows(self, workflows_table: WorkflowTable) -> None:
        workflows = await self.temporal.list_workflows()

        workflows_table.add_columns(*Workflow.columns())
        workflows_table.add_workflows(workflows)

        workflows_table.set_loading(False)

    async def on_workflow_table_workflow_selected(
        self, message: WorkflowTable.WorkflowSelected
    ) -> None:
        workflows_table = self.query_one("#workflows", WorkflowTable)
        workflows_table.display = False

        await self.mount(WorkflowView("workflow-view", message.workflow))


if __name__ == "__main__":
    app = TemporalTUI()
    app.run()
