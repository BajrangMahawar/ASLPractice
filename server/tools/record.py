import cv2
import pandas as pd
import mediapipe as mp

FORMAT_PATH = "./format.parquet"
OUTPUT_PATH = "./output/output.parquet"

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

def create_frame_landmark_df(results, frame, format):
    face = pd.DataFrame()
    pose = pd.DataFrame()
    left_hand = pd.DataFrame()
    right_hand = pd.DataFrame()

    if results.face_landmarks:
        for i, point in enumerate(results.face_landmarks.landmark):
            face.loc[i, ["x", "y", "z"]] = [point.x, point.y, point.z]
    if results.pose_landmarks:
        for i, point in enumerate(results.pose_landmarks.landmark):
            pose.loc[i, ["x", "y", "z"]] = [point.x, point.y, point.z]
    if results.left_hand_landmarks:
        for i, point in enumerate(results.left_hand_landmarks.landmark):
            left_hand.loc[i, ["x", "y", "z"]] = [point.x, point.y, point.z]
    if results.right_hand_landmarks:
        for i, point in enumerate(results.right_hand_landmarks.landmark):
            right_hand.loc[i, ["x", "y", "z"]] = [point.x, point.y, point.z]

    face = (
        face.reset_index()
        .rename(columns={"index": "landmark_index"})
        .assign(type="face")
    )
    pose = (
        pose.reset_index()
        .rename(columns={"index": "landmark_index"})
        .assign(type="pose")
    )
    left_hand = (
        left_hand.reset_index()
        .rename(columns={"index": "landmark_index"})
        .assign(type="left_hand")
    )
    right_hand = (
        right_hand.reset_index()
        .rename(columns={"index": "landmark_index"})
        .assign(type="right_hand")
    )

    landmarks = pd.concat([face, left_hand, pose, right_hand]).reset_index(drop=True)
    landmarks = format.merge(landmarks, on=["type", "landmark_index"], how="left")
    landmarks = landmarks.assign(frame=frame)
    return landmarks


def do_capture_loop(xyz):
    try:
        all_landmarks = []
        cap = cv2.VideoCapture(0)
        with mp_holistic.Holistic(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        ) as holistic:
            frame = 0
            while cap.isOpened():
                frame += 1
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)

                # Create landmark dataframe
                landmarks = create_frame_landmark_df(results, frame, xyz)
                all_landmarks.append(landmarks)

                # Draw landmark annotation on the image
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                mp_drawing.draw_landmarks(
                    image,
                    results.face_landmarks,
                    mp_holistic.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style(),
                )
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
                )
                mp_drawing.draw_landmarks(
                    image,
                    results.left_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                )
                mp_drawing.draw_landmarks(
                    image,
                    results.right_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style(),
                )

                cv2.imshow("MediaPipe Holistic", cv2.flip(image, 1))
                if cv2.waitKey(5) & 0xFF == 27:
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        return all_landmarks


if __name__ == "__main__":
    print("Start main")
    pq_file = FORMAT_PATH
    xyz = pd.read_parquet(pq_file)
    landmarks = do_capture_loop(xyz)
    landmarks = pd.concat(landmarks).reset_index(drop=True).to_parquet(OUTPUT_PATH)
