from typing import List, Optional
from ..prompts.evaluate_agents_prompt import AGENT_EVALUATOR_SYSTEM_PROMPT, AGENT_EVALUATOR_USER_PROMPT
from ..types import TaskResult, TextMessage, ToolCallExecutionEvent, ToolCallRequestEvent
from pydantic import BaseModel
import asyncio
import logging

logger = logging.getLogger(__name__)

class AgentToolDTO(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    method: str
    path: str
    jsonschema: dict
    auto_updated: bool = False

class AgentDTO(BaseModel):
    id: Optional[str] = None
    name: str
    system_prompt: str
    description: str
    base_url: str
    tools: List[AgentToolDTO] = []
    apispec_id: str
    updated_at: Optional[str] = None
    auto_updated: bool = False

class AgentEvaluation(BaseModel):
    id: str
    name: str
    description: str
    system_prompt: str
    tools: Optional[List[AgentToolDTO]] = None
    modified: bool

class EvaluationResponse(BaseModel):
    evaluation: List[AgentEvaluation]

class AgentEvaluatorService():
    def __init__(self, llm_service, agents_service):
        self.llm_service = llm_service
        self.agents_service = agents_service
        
    def needs_evaluation_task_result(self, task_result: TaskResult):
        for m in task_result.messages:
            if isinstance(m, TextMessage):
                if "error" in m.content.lower():
                    return True
            elif isinstance(m, ToolCallExecutionEvent):
                for f in m.content:
                    if f.is_error:
                        return True
            
        return False
    
    async def evaluate_task_result(self, agents: List[AgentDTO], task_result: TaskResult):
        asyncio.create_task(self._evaluate_task_result_impl(agents, task_result))
    
    async def _evaluate_task_result_impl(self, agents: List[AgentDTO], task_result: TaskResult):
        try:
            used_agents_str = []
            exec_result_str = []
            for m in task_result.messages:
                agent: AgentDTO | None = next((a for a in agents if a.name == m.source), None)
                if agent:
                    used_agents_str.append(agent.model_dump_json())

                    if isinstance(m, TextMessage):
                        exec_result_str.append("{}: {}".format(agent.name, m.content))
                    elif isinstance(m, ToolCallRequestEvent):
                        for f in m.content:
                            exec_result_str.append("{}: Calls function -> {} with args {} and id {}".format(agent.name, f.name, f.arguments, f.id))
                    elif isinstance(m, ToolCallExecutionEvent):
                        for f in m.content:
                            exec_result_str.append("{}: Call function with id {} (is_error: {}) returned -> {}".format(agent.name, f.call_id, f.is_error, f.content))
                        
            res = await self.llm_service.chat_completion('gpt-4o', [
                {
                    "role": "system",
                    "content": AGENT_EVALUATOR_SYSTEM_PROMPT
                }, {
                    "role": "user",
                    "content": AGENT_EVALUATOR_USER_PROMPT.format(agents="/n".join(used_agents_str), result="/n".join(exec_result_str))
                }
            ], False)
            
            result = EvaluationResponse.model_validate_json(res.choices[0].message.content)
            await self.update_from_evaluation(agents, result)
            return result
        except Exception as e:
            logger.error("Error evaluating and modifying response {}".format(e))
    
    async def update_from_evaluation(self, agents: List[AgentDTO], evaluation: EvaluationResponse):
        for ev in evaluation.evaluation:
            if ev.modified:
                o_agent = next((agent for agent in agents if agent.id == ev.id), None)
                if o_agent:
                    m_agent = AgentDTO(
                        id=ev.id,
                        name=ev.name,
                        apispec_id=o_agent.apispec_id,
                        base_url=o_agent.base_url,
                        system_prompt=ev.system_prompt,
                        description=ev.description,
                        tools=ev.tools
                    )
                    await self.agents_service.modify_agent_from_autoevaluation(m_agent.id, m_agent) 