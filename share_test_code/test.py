import ray
from test_ray_actor import Collaborator
from clone import Clone



collaborator_names = ['Portland', 'Seattle'] #, 'Chandler', 'Bangalore']

collaborators = []
collaborator_files = [
    "/home/parth-wsl/env_ray/test_ray_actor/config_collaborator_one.yaml",
    "/home/parth-wsl/env_ray/test_ray_actor/config_collaborator_two.yaml",
    "/home/parth-wsl/env_ray/test_ray_actor/config_collaborator_three.yaml",
    "/home/parth-wsl/env_ray/test_ray_actor/config_collaborator_four.yaml",
]
for collaborator_name, filename, resouces in zip(collaborator_names, collaborator_files, [0.6, 0.5]):
    temp = ray.remote(Collaborator)
    if resouces == 0.6:
        temp.options(num_cpus=resouces)
    else:
        temp.options(num_gpus=resouces)
    temp_actor = temp.remote(name=collaborator_name, collab_config=filename)
    temp_actor.initialize_private_attributes.remote()
    collaborators.append(temp_actor)
    
    del temp, temp_actor

clones = [Clone() for _ in range(len(collaborators))]
clones_dublicate = []

def merge_collab_and_clone(collab, clone):
    # collaborator private attributes (an example of large variable)
    print (f"Setting collaborator: {collab.name} private attributes as private attributes of clone:")
    print (f"Before setting clone.collab_private_attrs: {clone.collab_private_attrs}\n\n")
    clone.collab_private_attrs = collab.private_attributes
    print (f"After setting clone.collab_private_attrs: {clone.collab_private_attrs}\n\n")
    # An example of dynamically created variable
    clone.input = collab.name
    print (f"Dynamically created clone variable input: {clone.input}; has the same value as collab.name: {collab.name}")
    # An example of modification of existing variable
    print (f"Before setting clone.clone_private_attrs: {clone.clone_private_attrs}\n\n")
    clone.clone_private_attrs.update({'3': 'three', '4': 'four'})
    print (f"After setting clone.clone_private_attrs: {clone.collab_private_attrs}\n\n")
    # Removing collaborator private attrobutes from clone
    print ("Collaborator private attributes are no longer required")
    delattr(clone, "collab_private_attrs")
    print (f"Collab private attriubtes from clone is removed hasattr(clone, 'collab_private_attrs'): {hasattr(clone, 'collab_private_attrs')}")

    return clone

for i, (collab, clone) in enumerate(zip(collaborators, clones)):
    clone = ray.get(collab.exec.remote(cln=clone, func=merge_collab_and_clone))
    clones_dublicate.append(clone)

del collaborators

