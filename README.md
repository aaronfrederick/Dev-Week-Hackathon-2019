# Dev-Week-Hackathon-2019

I collaborated with @jdmendoza, @dynogravelso, and @stevay at the San Francisco Developer Week Hackathon to create the webapp in this repo. The webapp is a demo of a product that uses Clarifai's Image recognition API for home safety. 

Part One of the demo is an intruder alert system. The intruder alert system utilized Clarifai's face detection and face embedding models. The face detection model counts # of faces and the face embedding model creates a vector for each face. Using our LinkedIn we created ground truth vectors and stored them as references for comparison with new faces. To avoid curse of dimensionality with comparison, we used cosine similarity as comparison measure.

Part Two of the demo is a baby monitoring system. The baby monitor utilized general model API, which identifies different objects in a picture and labels them. We used the baby/toddler/child labels to determine if a baby is in frame and other labels to indicate danger i.e. fire/knives/toys.
