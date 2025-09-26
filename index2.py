import rich
import asyncio
from connection import config
from pydantic import BaseModel

from agents import (Agent, OutputGuardrailTripwireTriggered, Runner, 
    input_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered, output_guardrail

)
from pydantic import BaseModel

class SchoolCheck(BaseModel):
    is_unauthorized: bool
    school_name: str | None
    reasoning: str
from agents import Agent

gatekeeper_gr_agent = Agent(
    name="GateKeeper affiliation checker",
    instructions=(
        "Determine if the user is a student of a permitted school. "
        "If they say they attend a different school, set is_unauthorized = true. "
        "Otherwise false. Provide school_name and reasoning."
    ),
    output_type=SchoolCheck,
)
from agents import GuardrailFunctionOutput, InputGuardrailTripwireTriggered, Runner, trace
from agents.guardrail import input_guardrail
from agents.run_context import RunContextWrapper
from agents.items import TResponseInputItem
from connection import config

@input_guardrail
async def gatekeeper_guardrail(
    ctx: RunContextWrapper[None],
    agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(gatekeeper_gr_agent, input, context=ctx.context)
    out: SchoolCheck = result.final_output_as(SchoolCheck)
    
    return GuardrailFunctionOutput(
        output_info=out,
        tripwire_triggered=out.is_unauthorized,
    )
from agents import Agent

gatekeeper_agent = Agent(
    name="Gate Keeper",
    instructions=(
        "You respond to student queries only if they're from the permitted school. "
        "If guardrail trips, do not proceed."
    ),
    input_guardrails=[gatekeeper_guardrail],
)
async def main():
    try:
        await Runner.run(
            gatekeeper_agent,
            "Hello, I'm a student of Springfield High. Can I access school resources?"
        )
        print("Authorized: proceed with agent logic.")
    except InputGuardrailTripwireTriggered as e:
        print("Access denied: student from different school.")
        # In logs: e.output_info.schemaschool_name and reasoning
