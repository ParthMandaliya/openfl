import ray
from test_ray_actor import Collaborator
from clone import Clone


cpu = ray.remote(Collaborator(), num_gpus=0)
gpu = ray.remote(Collaborator(), num_gpus=1)


Collaborator_actor = ray.remote(Collaborator, )



collaborator_names = ['Portland', 'Seattle', 'Chandler', 'Bangalore']

collaborators = []
collaborator_files = [
    "/home/parth-wsl/env_ray/test_ray_actor/config_collaborator_one.yaml",
    "/home/parth-wsl/env_ray/test_ray_actor/config_collaborator_two.yaml",
    "/home/parth-wsl/env_ray/test_ray_actor/config_collaborator_three.yaml",
    "/home/parth-wsl/env_ray/test_ray_actor/config_collaborator_four.yaml",
]
for collaborator_name, filename in zip(collaborator_names, collaborator_files):
    temp = Collaborator_actor.remote(name=collaborator_name, collab_config=filename)
    temp.initialize_private_attributes.remote()
    collaborators.append(temp)
    del temp

clones = [Clone() for _ in range(len(collaborators))]
clones_dublicate = []

def merge_collab_and_clone(collab, clone):
    # collaborator private attributes (an example of large variable)
    print (f"Setting collaborator: {collab.name} private attributes as private attributes of clone:")
    print (f"Before setting clone.collab_private_attrs")
    clone.collab_private_attrs = collab.private_attributes
    # An example of dynamically created variable
    clone.input = collab.name
    # An example of modification of existing variable
    clone.clone_private_attrs.update({'3': 'three', '4': 'four'})
    
    print (f"clone.input {clone.input}; ")

    return clone

for i, (collab, clone) in enumerate(zip(collaborators, clones)):
    clone = ray.get(collab.exec.remote(cln=clone, func=merge_collab_and_clone))
    clones_dublicate.append(clone)

# del collaborators

for clone in clones_dublicate:
    print(f"Clone name: '{clone.input}' is dynamically created; modified clone private attributes: {clone.clone_private_attrs}; and clone has private attributes: {clone.collab_private_attrs}\n")

