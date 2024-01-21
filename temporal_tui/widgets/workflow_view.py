import textual.app
import textual.containers as containers
import textual.widgets as widgets

from temporal_tui.models import Workflow
from temporal_tui.service import TemporalService
from temporal_tui.widgets import (
    WorkflowInputAndResults,
    WorkflowRelationships,
    WorkflowSummary,
)


class WorkflowView(widgets.Static):
    def __init__(self, id: str, workflow: Workflow) -> None:
        self.workflow = workflow
        super().__init__(id=id)

    def compose(self) -> textual.app.ComposeResult:
        yield widgets.Label(self.workflow.id)

        yield containers.ScrollableContainer(
            WorkflowSummary(id="workflow-summary", workflow=self.workflow),
            WorkflowRelationships(id="workflow-relationships", workflow=self.workflow),
            WorkflowInputAndResults(
                id="workflow-input-and-results", workflow=self.workflow
            ),
            widgets.DataTable(id="workflow-event-history"),
        )

    def on_mount(self) -> None:
        self.temporal = TemporalService.from_env()

        event_history_table = self.query_one(
            "#workflow-event-history", widgets.DataTable
        )
        event_history_table.cursor_type = "row"
        event_history_table.loading = True

        self.load_event_history(event_history_table)

    @textual.work
    async def load_event_history(self, table: widgets.DataTable) -> None:
        history = await self.temporal.fetch_workflow_history(self.workflow)

        table.add_columns("", "Date & Time", "Event Type", "")

        for event in history.events:
            table.add_row(
                event.event_id,
                event.event_time.ToDatetime().ctime(),
                event.event_type,
                "",
            )

        table.loading = False
