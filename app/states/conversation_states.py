from aiogram.fsm.state import State, StatesGroup
# FSM States for conversation flow
class ConversationStates(StatesGroup):

    waiting_for_question = State()

