import mediapipe as model


class HandDetection:
    def __init__(self, static_image_mode=False, max_num_hands=1, model_complexity=1, min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.modelHands = model.solutions.hands
        self.Hands = self.modelHands.Hands(static_image_mode=self.static_image_mode,
                                           max_num_hands=self.max_num_hands,
                                           model_complexity=self.model_complexity,
                                           min_detection_confidence=self.min_detection_confidence,
                                           min_tracking_confidence=self.min_tracking_confidence)
        self.handsDraw = model.solutions.drawing_utils

    def detectedHands(self, frame):
        results = self.Hands.process(frame)
        return results.multi_hand_landmarks

    def drawDetection(self, frame, landmarks):
        self.handsDraw.draw_landmarks(frame, landmarks, self.modelHands.HAND_CONNECTIONS)
