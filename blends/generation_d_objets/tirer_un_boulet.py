from bge import logic

# Recuperer la scene
scene = logic.getCurrentScene()

# Recuperer le canon
canon = scene.objects["Canon"]

# Recuperer le boulet sur sa couche invisible
boulet = scene.objectsInactive["Boulet"]

# Creer une instance de boulet 
instance = scene.addObject(boulet, canon, 0)

# Donner une vitesse aux instances
instance.localLinearVelocity.z = -10.0
