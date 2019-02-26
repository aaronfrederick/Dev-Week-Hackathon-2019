from clarifai.rest import ClarifaiApp
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle


def intruder(filename,api_key):
    faces = []
    #intantiate important objects
    app = ClarifaiApp(api_key=api_key)
    is_face_model = app.public_models.face_detection_model
    model = app.public_models.face_embedding_model
    reference_vectors = pickle.load(open('data/reference_vectors.pkl', 'rb'))

    #check to see if there is a face
    is_face_data = is_face_model.predict_by_filename(filename)
    is_face = is_face_data['outputs'][0]['data']

    #if there is a face, see who it is
    if is_face:
        test_vector = model.predict_by_filename(filename)

        list_of_vecs = test_vector['outputs'][0]['data']['regions']
        vecs = [np.array(x['data']['embeddings'][0]['vector']) for x in list_of_vecs]

        for tv in vecs:
            sims = cosine_similarity(reference_vectors, [tv])
            names = ['Aaron', 'Ben', 'Danny', 'Steve']

            max_val = 0
            for i, val in enumerate(sims):
                if val > max_val:
                    max_val = val
                    name_index = i

            if max_val > 0.6:
                #print(names[i])
                faces.append(names[i])
            else:
                #print("No Matches")
                faces.append('Not a Match')
        for s in list(set(faces)):
            if s in names:
                return len(faces), True
        return len(faces), False
    return 0, True
