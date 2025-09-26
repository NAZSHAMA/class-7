from pydantic import BaseModel
from agents import Agent, Runner, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from agents.guardrail import input_guardrail
from agents.run_context import RunContextWrapper
from connection import config

class ColdRunCheck(BaseModel):
    is_too_cold: bool
    temperature_celsius: float
    reasoning: str

# Guardrail agent to inspect temperature mention
guardrail_agent = Agent(
    name="AC_run checker",
    instructions=(
        "Return a ColdRunCheck indicating if the user is asking to run "
        "when the temperature is below 26 °C. "
        "Interpret input to extract temperature, or ask 'What's the temperature?' "
        "if not mentioned."
    ),
    output_type=ColdRunCheck,
)

@input_guardrail
async def father_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input: str | list
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    output = result.final_output_as(ColdRunCheck)
    too_cold = output.is_too_cold
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=too_cold,
    )

father_agent = Agent(
    name="Father",
    instructions=(
        "You're a caring father. You respond to child's requests. "
        "But if the guardrail trips because it's too cold (< 26 °C), you don't proceed."
    ),
    input_guardrails=[father_guardrail],
)
async def main():
    try:
        await Runner.run(father_agent, "Dad, can I go for a run? It's 22 °C outside.")
        print("Child allowed to run.")
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail tripped: too cold to run.")
        # In logs: would show output_info with temperature and reasoning
