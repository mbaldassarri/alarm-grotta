# -*- coding: utf-8 -*-
import logging
import ask_sdk_core.utils as ask_utils
import random
import re
import requests
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_PATH = 'http://your_server_path:port/alarm'
DEFAULT_TURN_ON_MINS = "5"
ON = "on"
OFF = "off"

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Ciao! Chiedimi di accendere o spegnere l'allarme. Puoi specificare tra quanti minuti cambiare lo stato."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class TurnOnIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("TurnOnAlarmIntent")(handler_input)

    def handle(self, handler_input):
        time_slot = handler_input.request_envelope.request.intent.slots['time'].value
        if time_slot:
            minutes = re.findall(r'\d+', time_slot)[0]  #get mins from Amazon Duration Slot
        else:
            minutes = DEFAULT_TURN_ON_MINS
        
        speak_output = ["Metto in sicurezza la tua casa tra " + minutes + " minuti. Confermi? ", "Accendo l'allarme tra " + minutes + " minuti! Ho capito bene?",
                        "Accendo l'allarme tra "+ minutes + " minuti a partire da adesso. Confermi?"]

        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["status"] = ON
        session_attr["delay"] = minutes
        
        return (
            handler_input.response_builder
                .speak(random.choice(speak_output))
                .ask("Mi è stato chiesto di accendere l'allarme di casa tra " + str(minutes) + " minuti! Procedo?")
                .response
        )


class TurnOffIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("TurnOffAlarmIntent")(handler_input)

    def handle(self, handler_input):
        
        speak_output = "Mi è stato chiesto di spegnere l'allarme. Confermi?"
        
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["status"] = OFF
        session_attr["delay"] = "0"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Posso procedere con lo spegnimento dell'allarme?")
                .response
        )



class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        if "status" in session_attr:
            status = session_attr["status"]
            delay = session_attr["delay"]
            if status == ON:
                if delay:
                    requests.get(BASE_PATH, params={'status': ON, 'delay': delay})
                speak_on_output = "Ok, imposto accensione tra "+ delay + " minuti"
                return (handler_input.response_builder.speak(speak_on_output).response)
            elif status == OFF:
                if delay:
                    requests.get(BASE_PATH, params={'status': OFF, 'delay': delay})
                speak_on_output = "Ok, spengo l'allarme!"
                return (handler_input.response_builder.speak(speak_on_output).response)
            else:
                speak_on_output = "Mi dispiace, si è verificato un errore interno. Si prega di utilizzare l'app per accendere l'allarme."
                return (handler_input.response_builder.speak(speak_on_output).response)


class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        return (
            handler_input.response_builder
                .speak("D'accordo, ripetimi se devo accendere o spegnere")
                .ask("In che stato vuoi mettere l'allarme?")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        first_speak_output = "Puoi decidere se accendere o spegnere l'allarme di casa semplicemente dicendo: Alexa, accendi l'allarme di casa"
        second_speak_output = "Semplicemente pronuncia: accendi allarme. Oppure: spegni allarme di casa"
        return (
            handler_input.response_builder
                .speak(first_speak_output)
                .ask(second_speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Arrivederci a presto"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Mi dispiace ma non ho capito. Prova ancora"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(TurnOnIntentHandler())
sb.add_request_handler(TurnOffIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()