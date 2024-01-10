
import textual
import textual.app
import textual.widgets as widgets

from temporal_tui.models import Workflow
from temporal_tui.service import TemporalService


class TemporalTUI(textual.app.App):
    def compose(self) -> textual.app.ComposeResult:
        yield widgets.DataTable()

    def on_mount(self) -> None:
        self.temporal = TemporalService.from_env()

        table = self.query_one(widgets.DataTable)
        table.zebra_stripes = True
        table.loading = True

        self.load_workflows(table)

    @textual.work
    async def load_workflows(self, data_table: widgets.DataTable) -> None:
        workflows = await self.temporal.list_workflows()

        data_table.add_columns(*Workflow.columns())
        data_table.add_rows([workflow.as_cells() for workflow in workflows])

        data_table.loading = False


if __name__ == "__main__":
    app = TemporalTUI()
    app.run()
