import orjson
import rich.syntax
import textual.app
import textual.containers as containers
import textual.widgets as widgets

from temporal_tui.models import Workflow


class WorkflowSummary(widgets.Static):
    DEFAULT_CSS = """
    #execution-details {
        height: 5;
    }

    #execution-details Label {
        height: 1;
    }

    #execution-details Rule {
        height: 1;
    }

    #task-queue {
        height: 5;
    }

    #task-queue Label {
        height: 1;
    }

    #task-queue Rule {
        height: 1;
    }

    #times {
        height: 5;
    }

    #times Label {
        height: 1;
    }

    #times Rule {
        height: 1;
    }
    """

    def __init__(self, id: str, workflow: Workflow) -> None:
        self.workflow_type = workflow.workflow_type
        self.close_time = workflow.close_time or ""
        self.start_time = workflow.start_time
        self.run_id = workflow.run_id
        self.task_queue = workflow.task_queue
        self.history_length = workflow.history_length
        self.search_attributes = workflow.search_attributes
        super().__init__(id=id)

    def compose(self) -> textual.app.ComposeResult:
        with widgets.Collapsible(title="Summary"):
            with containers.HorizontalScroll():
                with containers.Vertical(id="execution-details"):
                    yield widgets.Label("Execution Details")
                    yield widgets.Rule()

                    yield widgets.Label(f"Workflow Type {self.workflow_type}")
                    yield widgets.Label(f"Run ID {self.run_id}")
                    yield widgets.Label(
                        f"History Size (Number of events) {self.history_length}"
                    )

                with containers.Vertical(id="task-queue"):
                    yield widgets.Label("Task Queue")
                    yield widgets.Rule()

                    yield widgets.Label(f"{self.task_queue}")

                with containers.Vertical(id="times"):
                    yield widgets.Label("Start & Close Time")
                    yield widgets.Rule()

                    yield widgets.Label(f"Start Time {self.start_time}")
                    yield widgets.Label(f"Close Time {self.close_time}")

            with containers.VerticalScroll():
                yield widgets.Label("Search Attributes")
                yield widgets.Rule()

                yield widgets.RichLog(
                    id="search-attributes-log", highlight=True, markup=True
                )

    def on_mount(self) -> None:
        text_log = self.query_one("#search-attributes-log", widgets.RichLog)

        search_attributes_json = orjson.dumps(
            self.search_attributes, option=orjson.OPT_INDENT_2
        ).decode("utf-8")
        text_log.write(rich.syntax.Syntax(search_attributes_json, "json"))
