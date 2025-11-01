import mediapipe as model


class EyeDetection:
    def __init__(self, static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        self.static_image_mode = static_image_mode
        self.max_num_faces = max_num_faces
        self.refine_landmarks = refine_landmarks
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.FaceModel = model.solutions.face_mesh
        self.Faces = self.FaceModel.FaceMesh(static_image_mode=False, max_num_faces=1,
                                             refine_landmarks=True,
                                             min_detection_confidence=0.5,
                                             min_tracking_confidence=0.5)
        self.draw = model.solutions.drawing_utils

    def detectEyes(self, frame):
        result = self.Faces.process(frame)
        return result.multi_face_landmarks

    def drawDetection(self, frame, landmarks):
        self.draw.draw_landmarks(frame, landmarks, self.FaceModel.FACEMESH_LEFT_IRIS)
        # self.draw.draw_landmarks(frame, landmarks, self.FaceModel.FACEMESH_LEFT_EYE)
