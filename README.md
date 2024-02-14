# Structure_2D
This is a basic 2D Structural analysis program in python. It is capable of analyzing frames and trusses.

## **How to use it?**
These are the General Steps:
1. Import requirements
2. Create Nodes
3. Create Elements
4. Create Supports
5. Add Loads
6. Create Structure and assign nodes, elements, supports.
7. Run Analysis

### Importing requirements


First import everything from `Structure_2D.Core`, which is better than importing everything one by one.

```
from Structure_2D.Core import *
```

This step is a little problematic and may not work so try this for now, even though this is bulky:
```
from Core.CrossSection import *
from Core.Element import *
from Core.Node import Node
from Core.Load import *
from Core.Material import *
from Core.StructureGlobal import *
from Core.Support import *
```
### Creating Nodes
Next you need to create `Node` instances to act as -well- nodes. We will store all node instances in an array:

```
nodes: list[Node] = []
nodes.append(Node(x=0, y=0, idnum=0))
nodes.append(Node(x=0, y=10, idnum=1))
nodes.append(Node(x=10, y=10, idnum=2))
```

### Creating Elements
Next up we create `GeneralFrameElement2D` instances, which is a lot to type, but thankfully you won't be needing it 
directly. You only really need either a `FrameElement` or `TrussElement`:

```
elements: list[GeneralFrameElement2D] = []
elements.append(FrameElement(i=nodes[0], j=nodes[1]))
elements.append(FrameElement(i=nodes[1], j=nodes[2]))
```

### Creating Supports

Next we create the supports for our structure, using a `Support` instance:
```
supports: list[Support] = []
supports.append(FixedSupport(node=nodes[0], support_num=0))
```

There are three kinds of supports available: `FixedSupport`, `PinnedSupport`, and `RollerSupport`. Note that 
`RollerSupport` restrains translation in the y-axis. A roller support that restrains translation in x-axis exists, but not in 
a user-friendly way yet, use the following line:
```
Support(node=nodes[0], support_num=0, support_type: str = 'roller-x')
```

Adjust to whatever nodes your structure has.

### Adding Materials

Ah, we forgot to talk about materials, and cross-sections.
The base types are `Material`, and `CrossSection`.

However, to create a material or cross-section, do the following:
```
material1 = NewMaterial()
crossSection1 = NewCrossSection()
```
Check documentation in [Material.py](/Core/Material.py) and [CrossSection.py](Core/CrossSection.py) for each class to see what parameters are required. However, since a lot of functionality is not yet
implemented, and people usually are in a hurry, do the following:
```
material2 = TestMaterial(E=200000000)
crossSection2 = TestRectangularCrossSection(A=0.25, I=0.035)
```

To Apply the material, just use the `.setMaterial()`, or `setCrossSection()` call from an element/member.
```
elements[0].setMaterial(material2)
elements[1].setCrossSection(crossSection2)
```

Don't worry, the elements are initialized with a default material and cross-section. If you want to apply it to all 
elements, simply loop over them and use the call.

### Creating the Structure

Now let us talk about the structure itself. We require the `StructureGlobal` class:
```
structure: StructureGlobal = StructureGlobal()
structure.nodes = nodes
structure.elements = elements
structure.supports = supports
```

This creates a structure object and passes the nodes, elements, and supports we have created until now. Be careful, 
because they require arrays.  

### Sidenote: Loads
Hold on, where are the loads?  
Don't worry.  

There are two load types you need to know, `MemberLoad` and `NodeLoad`, which can be applied on members and nodes only
respectively.
Also, the only load type that can be used currently is `StaticLoad`.  

Confused?  
Don't be. You are not going to be using those three anyway, that is background info, also they can't be instantiated.

The loads you need are the following:  
+ `PointLoad`,`MomentLoad`, which are of type `NodeLoad`.  
+ `PointLoadMember`,`MomentLoadMember`, `UniformDistributedLoad`, `VaryingDistributedLoad`, `TrapezoidalDistributedLoad`, 
which are of type `MemberLoad`.

Make a little sense?
Good.

### Applying Loads
Now we apply loads to our structure:
```
elements[1].addLoad(UniformDistributedLoad(magnitude=10, start_location=2, end_location=7))
nodes[1].addLoad(PointLoad(magnitude=100, angle=0))
```

If you're wondering why we're not applying loads to `structure.elements[1]`, its because it's too long to type, also the
`elements` array and `structure.elements` array refer to the same array object which contain the same `GeneralFrame2D`
objects anyway. So, no harm done. It's all good, man.

Check initialization parameters for each load type from [Load.py](Core/Load.py)

### Run Analysis
Now what you've been waiting for, running the analysis:
```
structure.runAnalysis()
```

LOL, anticlimactic innit?

### Print Results
Where are the results?

```
print(structure.resultSummary())
```

This is it fellows.

There is more stuff, but it hasn't been cleanly implemented for the end user.
Member End Forces, Shear Diagrams, Moments Diagrams, etc.
Will update this file when I do, if i don't forget.
The structure formed in this readme file can be found in [ReadmeBuilder.py](/Builder/ReadmeBuilder.py)