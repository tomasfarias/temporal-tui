import collections.abc

import rich.repr
import rich.text
import textual.message as message
import textual.widgets as widgets
import textual.widgets.data_table as data_table

from temporal_tui.models import Workflow


class WorkflowTable(widgets.DataTable):
    """A DataTable of Temporal Workflows."""
    DEFAULT_CSS = """
    WorkflowTable {
        height: auto;
        max-height: 100vh;
    }
    """

    class WorkflowSelected(message.Message):
        """Posted when a Workflow is selected.

        This message is only posted when the
        `cursor_type` is set to `"row"`. Can be handled using
        `on_data_table_row_selected` in a subclass of `DataTable` or in a parent
        widget in the DOM.
        """

        def __init__(
            self,
            workflow: Workflow,
            workflow_table: "WorkflowTable",
            cursor_row: int,
            row_key: data_table.RowKey,
        ) -> None:
            self.workflow: Workflow = workflow
            """The Workflow that was selected."""
            self.workflow_table = workflow_table
            """The workflow table."""
            self.cursor_row: int = cursor_row
            """The y-coordinate of the cursor that made the selection."""
            self.row_key: data_table.RowKey = row_key
            """The key of the row that was selected."""
            super().__init__()

        def __rich_repr__(self) -> rich.repr.Result:
            yield "cursor_row", self.cursor_row
            yield "row_key", self.row_key

    def __init__(self, name: str | None = None, id: str | None = None) -> None:
        self.workflows: dict[data_table.RowKey, Workflow] = {}
        super().__init__(name=name, id=id, cursor_type="row")

    def add_workflow(
        self,
        workflow: Workflow,
        height: int = 1,
        label: rich.text.TextType | None = None,
    ) -> data_table.RowKey:
        row_key = self.add_row(
            *workflow.as_cells(), height=height, key=workflow.run_id, label=label
        )
        self.workflows[row_key] = workflow

        return row_key

    def add_workflows(
        self, workflows: collections.abc.Iterable[Workflow]
    ) -> list[data_table.RowKey]:
        row_keys = []

        for workflow in workflows:
            row_key = self.add_workflow(workflow)
            row_keys.append(row_key)

        return row_keys

    async def on_data_table_row_selected(
        self, message: widgets.DataTable.RowSelected
    ) -> None:
        self.post_message(
            WorkflowTable.WorkflowSelected(
                self.workflows[message.row_key],
                self,
                message.cursor_row,
                message.row_key,
            )
        )

        message.stop()
