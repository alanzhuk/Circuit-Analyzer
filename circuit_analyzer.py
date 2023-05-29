import sympy #for the systems of equations for node voltage
import xlrd #reads an excel doc
bat = ""#main battery

class ground:
    #gets location values
    x = 0
    y = 0           
class resistor:
    #gets basic values
    name = ""
    i = 0 
    v = 0
    r = 0
    def __init__(self,loc_name,loc_r):
        self.r = loc_r
        self.name = loc_name
class battery: #holds all the logistics for the battery but does not get drawn
    #gets basic values
    name = ""
    i = 0 
    v = 0
    r = 0
    paired = []#stores what it's paired to
    def __init__(self,loc_name,loc_v):
        self.name = loc_name
        self.v = loc_v
class battery_top: #positive terminal
    paired = "" #stores what it is paired to - when the wire is linked it will pair to the main thing instead of the top or bottom
class battery_bottom: #negative terminal
    paired = "" #stores what it is paired to - when the wire is linked it will pair to the main thing instead of the top or bottom
class CSource: #current source(holds all thee logistics for the current source, but does not get drawn)
    #gets basic values
    name = ""
    i = 0
    paired = []#stores what it's paired to
    def __init__(self,loc_name,loc_i):
        self.name = loc_name
        self.i = loc_i
class CSource_top:
    paired = "" #stores what it is paired to - when the wire is linked it will pair to the main thing instead of the top or bottom
class CSource_bottom:
    #gets location values
    paired = "" #stores what it is paired to - when the wire is linked it will pair to the main thing instead of the top or bottom
class wire:
    #gets basic values
    i = 0 
    v = 0 #not voltage drop, but node voltage
    name = ""
    connections = []#checks what the wires are connected to. 
##    def draw(self): #draws the wire
    def __init__(self,loc_name,con):
        self.name = loc_name
        self.connections = con

def bordering(e, orig): #returns everything that is bordering resistor e. orig is the original wire.
    for i in catalog:
        if isinstance(i,wire):
            if e in i.connections and i != orig:
                return i
    
def node_voltage():
    for i in catalog:
        if isinstance(i,battery):
            bat = i
    wires = [] #combines all the wires together
    gWire = "" #caches which wire is attached to ground
    vWire = "" #caches which wire is attached to the positive terminal of the main battery
    equations = [] #stores all the equations for the system
    eq_cache = ""#stores the equation as we make it. 
    #groups all the wires in one dictionary to make node voltage analysis easier
    for i in catalog:
        if isinstance(i,wire):
            wires.append(i)
            for w in i.connections:
                if isinstance(w,ground):
                    gWire = i
                    i.v = 0
                elif isinstance(w,battery_top): #when I upgrade it to be able to solve super circuits, I need to made sure that it is pulling from the battery with ground in it.
                    vWire = i
                    i.v = bat.v
    var = { #ties each wire to a variable - NOTE - I'm pretty sure that var doesn't mean anything in python, but if there is an error it might be this. 

    }
    count = 0
    pos = ["x","y","z","a"] #possible variables
    #assigning variables to wires
    for i in wires:
        if gWire != i and vWire != i:
                var[i] = pos[count]
                count += 1
        if gWire == i:
                var[i] = 0
        if vWire == i:
                var[i] = bat.v
    if len(wires) == 4:
        x, y = sympy.symbols(['x','y'])
    elif len(wires) == 5:
        x, y, z = sympy.symbols(['x','y','z'])
    elif len(wires) == 6:
        x, y, z, a = sympy.symbols(['x','y','z','a'])
    #setting up equations
    for i in wires:
        eq_cache = ""
        if gWire != i and vWire != i:
            for w in i.connections:
                if isinstance(w,resistor):
                    if gWire == bordering(w,i):
                        eq_cache = eq_cache + "+" + "(" + var[i] + "/" + str(w.r) + ")"
                    elif vWire == bordering(w,i):
                        eq_cache = eq_cache + "+" + "(" + var[i] + "-" + str(vWire.v) + ")/" + str(w.r)
                    else:
                        eq_cache = eq_cache + "+" + "(" + var[i] + "-" + var[bordering(w,i)] + ")/" + str(w.r)
                elif isinstance(w,CSource_bottom):
                    eq_cache = eq_cache + "+" + str(w.paired.i)
                elif isinstance(w,CSource_top):
                    eq_cache = eq_cache + "-" + str(w.paired.i)
            equations.append(sympy.Eq(eval(eq_cache), 0))
    if len(wires) == 4:
        cache = sympy.linsolve(equations,[x, y])
    elif len(wires) == 5:
        cache = sympy.linsolve(equations,[x, y, z])
    elif len(wires) == 6:
        cache = sympy.linsolve(equations,[x, y, z, a])
    #sympy returns a weird string so this isolates it and puts it into a list
    save = ""
    paren = 0 #counts the amount of open perenthesis, because it has 2 parenthesis before giving the actual values I want
    start = False
    ret = []#returns the values
    for i in str(cache):
        if i == "(" and paren != 0:
            start = True
        elif start and i != "," and i != ")" and paren != 0:
            save = save + str(i)
        elif i == ",":
            ret.append(float(save))
            save = ""
        elif i == ")":
            ret.append(float(save))
            break
        paren += 1
    count = 0         
    for i in wires:
        if gWire != i and vWire != i:
                i.v = ret[count]
                count += 1
    #finds voltage drops and current
    for i in wires:
        for w in i.connections:
            if isinstance(w,resistor):
                w.v = abs(i.v - bordering(w,i).v)
                w.i = w.v/w.r
    #finds battery current
    for i in wires:
        for w in i.connections:
            if isinstance(w,battery_top):
                cache = i #using cache to store which wire touches the battery
    for i in cache.connections:
        if isinstance(i,resistor):
            bat.i = bat.i + i.i
    #finds total resistance
    bat.r = bat.v / bat.i
def wire_find(name):#finds what the wire is connected to while parsing. This uses the name variable to search for the element.
    cache = []#caches list of connections.
    for i in catalog:
        name_top = i.name + "_top"
        name_bottom = i.name + "_bottom"
        if isinstance(i,ground):
            pointless_break = 12
        elif name == str(i.name):
            return(i)
        elif name == name_bottom:
            if isinstance(i,battery):
                for w in i.paired:
                    if isinstance(w,battery_bottom):
                        return(w)
            if isinstance(i,CSource):
                for w in i.paired:
                    if isinstance(w,CSource_bottom):
                        return(w)
        elif name == name_top:
            if isinstance(i,battery):
                for w in i.paired:
                    if isinstance(w,battery_top):
                        return(w)
            if isinstance(i,CSource):
                for w in i.paired:
                    if isinstance(w,CSource_top):
                        return(w)
def parse_doc(loc):
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0) 
    sheet.cell_value(0, 0)

    for i in range(sheet.nrows):
        if str(sheet.cell_value(i,0)) == 'battery':
            catalog.append(battery(sheet.cell_value(i,1),sheet.cell_value(i,2)))
            catalog[len(catalog)-1].paired.append(battery_top())
            catalog[len(catalog)-1].paired.append(battery_bottom())
            for w in catalog[len(catalog)-1].paired:
                w.paired = catalog[len(catalog)-1]
        elif str(sheet.cell_value(i,0)) == 'CSource':
            catalog.append(CSource(sheet.cell_value(i,1),sheet.cell_value(i,2)))
            catalog[len(catalog)-1].paired.append(CSource_top())
            catalog[len(catalog)-1].paired.append(CSource_bottom())
            for w in catalog[len(catalog)-1].paired:
                w.paired = catalog[len(catalog)-1]    
        elif str(sheet.cell_value(i,0)) == 'resistor':
            catalog.append(resistor(sheet.cell_value(i,1),sheet.cell_value(i,2)))
        elif str(sheet.cell_value(i,0)) == 'ground':
            catalog.append(ground())
        elif str(sheet.cell_value(i,0)) == 'wire':
            cache = []
            for z in range(sheet.ncols):
                if str(sheet.cell_value(i,z)) == "ground":
                    cache.append(ground())
                else:
                    cache.append(wire_find(sheet.cell_value(i,z)))
            catalog.append(wire(sheet.cell_value(i,1),cache))
#functions that run after a button is clicked
catalog = [] #catalogs all of the elements in the circuit. For now I think I will just make the keys 1,2,3..., but if I need to change it along the line I will specify like wire1,battery2,resistor1 or stuff like that
#temporary note for test: wire 1 = top of battery; wire 2 = cross; wire 4 = ground, wire 3 = other
parse_doc(input("put in file location(note, must be an xlsx file. Each collumn should correspond with an element. The first row should be the type of element[wire,battery,CSource,resistor,ground]. The second row should have the name of the element. For everything but wire, the third row should have the known characteristic. For wires the rest of the rows are for connections. NOTE: wires must always be last."))
node_voltage()
for i in catalog:
    if isinstance(i,wire):
        print("wire " + str(i.name) +"   -   " + "v=" + str(i.v) + "volts")
    if isinstance(i,battery):
        print("battery " + str(i.name) +"   -   " + "v=" + str(i.v) + "volts" + "  i=" + str(i.i) + "Amps")
    if isinstance(i,resistor):
        print("resistor " + str(i.name) +"   -   " + "v=" + str(i.v) + "volts" + "  i=" + str(i.i) + "Amps")


    
