import datetime as dt
import enum

import attrs
import rich.text
import temporalio.client


class WorkflowStatus(str, enum.Enum):
    CANCELED = "Canceled"
    COMPLETED = "Completed"
    CONTINUED_AS_NEW = "Continued-As-New"
    FAILED = "Failed"
    NONE = "None"
    RUNNING = "Running"
    TERMINATED = "Terminated"
    TIMED_OUT = "Timed-Out"

    @classmethod
    def from_workflow_execution(cls, execution: temporalio.client.WorkflowExecution):
        status = execution.status

        match status:
            case temporalio.client.WorkflowExecutionStatus.CANCELED:
                return WorkflowStatus.CANCELED
            case temporalio.client.WorkflowExecutionStatus.COMPLETED:
                return WorkflowStatus.COMPLETED
            case temporalio.client.WorkflowExecutionStatus.CONTINUED_AS_NEW:
                return WorkflowStatus.CONTINUED_AS_NEW
            case temporalio.client.WorkflowExecutionStatus.FAILED:
                return WorkflowStatus.FAILED
            case temporalio.client.WorkflowExecutionStatus.RUNNING:
                return WorkflowStatus.RUNNING
            case temporalio.client.WorkflowExecutionStatus.TERMINATED:
                return WorkflowStatus.TERMINATED
            case temporalio.client.WorkflowExecutionStatus.TIMED_OUT:
                return WorkflowStatus.TIMED_OUT

            case None:
                return WorkflowStatus.NONE


WorkflowColumns = tuple[str, str, str, str, str, str, str]
WorkflowCells = tuple[
    rich.text.Text,
    rich.text.Text,
    rich.text.Text,
    rich.text.Text,
    rich.text.Text,
    rich.text.Text,
    rich.text.Text,
]


@attrs.define
class Workflow:
    """Models a Temporal Workflow for display."""

    id: str
    run_id: str
    workflow_type: str
    status: WorkflowStatus
    start_time: dt.datetime
    execution_time: dt.datetime | None
    close_time: dt.datetime | None

    @classmethod
    def from_workflow_execution(cls, execution: temporalio.client.WorkflowExecution):
        status = WorkflowStatus.from_workflow_execution(execution)
        return cls(
            id=execution.id,
            run_id=execution.run_id,
            workflow_type=execution.workflow_type,
            status=status,
            start_time=execution.start_time,
            execution_time=execution.execution_time,
            close_time=execution.close_time,
        )

    @staticmethod
    def columns() -> WorkflowColumns:
        return (
            "Id",
            "Run Id",
            "Workflow Type",
            "Status",
            "Start Time",
            "Execution Time",
            "Close Time",
        )

    def as_cells(self) -> WorkflowCells:
        return (
            rich.text.Text(self.id, justify="left"),
            rich.text.Text(self.run_id, justify="left"),
            rich.text.Text(self.workflow_type, justify="left"),
            rich.text.Text(self.status, justify="left"),
            rich.text.Text(self.start_time.ctime(), justify="right"),
            rich.text.Text(
                self.execution_time.ctime() if self.execution_time is not None else "",
                justify="right",
            ),
            rich.text.Text(
                self.close_time.ctime() if self.close_time is not None else "",
                justify="right",
            ),
        )
