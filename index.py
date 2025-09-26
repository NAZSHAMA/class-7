from pydantic import BaseModel
from agents import Agent, Runner, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from agents.guardrail import input_guardrail
from agents.run_context import RunContextWrapper
from agents.items import TResponseInputItem
from connection import config

class ScheduleChangeOutput(BaseModel):
    is_schedule_change: bool
    reasoning: str

guardrail_agent = Agent(
    name="Schedule change detector",
    instructions="Detect if the user is asking to change their class timings or schedule.",
    output_type=ScheduleChangeOutput,
)
@input_guardrail
async def schedule_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    output = result.final_output_as(ScheduleChangeOutput)

    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=output.is_schedule_change,
    )
agent = Agent(
    name="Student Assistant",
    instructions="You help students with school-related queries, except schedule change requests.",
    input_guardrails=[schedule_guardrail],
)
async def main():
    try:
        await Runner.run(agent, "I want to change my class timings 😭😭")
        print("Guardrail didn't trip — agent proceeded unexpectedly.")
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail tripped: schedule change request was blocked.")
