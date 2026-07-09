import xml.etree.ElementTree as ET
import json
import math


inp = "model.rbxmx"
out = "output.json"

parts = []


def prop(props, name):
    name = name.lower()

    for x in props:
        if x.attrib.get("name", "").lower() == name:
            return x

    return None



def num(node, name, default=0):

    if node is None:
        return default

    if name in node.attrib:
        return float(node.attrib[name])

    val = node.findtext(name)

    if val:
        return float(val)

    return default



def vec(node):

    if node is None:
        return [0, 0, 0]

    return [
        num(node, "X"),
        num(node, "Y"),
        num(node, "Z")
    ]



def color(node):

    if node is None:
        return "ffffff"

    try:
        if node.tag == "Color3uint8":
            val = int(node.text)

            r = (val >> 16) & 255
            g = (val >> 8) & 255
            b = val & 255

            return f"{r:02x}{g:02x}{b:02x}"

    except:
        pass

    return "ffffff"



def value(node, default=""):

    if node is None:
        return default

    if node.text:
        return node.text

    return node.attrib.get(
        "value",
        default
    )



def cframe(node):

    if node is None:
        return [0, 0, 0], [0, 0, 0]


    pos = [
        float(node.findtext("X", 0)),
        float(node.findtext("Y", 0)),
        float(node.findtext("Z", 0))
    ]


    r00 = float(node.findtext("R00", 1))
    r01 = float(node.findtext("R01", 0))
    r02 = float(node.findtext("R02", 0))

    r10 = float(node.findtext("R10", 0))
    r11 = float(node.findtext("R11", 1))
    r12 = float(node.findtext("R12", 0))

    r20 = float(node.findtext("R20", 0))
    r21 = float(node.findtext("R21", 0))
    r22 = float(node.findtext("R22", 1))


    if abs(r21) < 0.999999:
        x = math.asin(-r21)
        y = math.atan2(r20, r22)
        z = math.atan2(r01, r11)

    else:
        x = math.copysign(math.pi / 2, -r21)
        y = math.atan2(-r02, r00)
        z = 0


    rot = [
        math.degrees(x),
        math.degrees(y),
        math.degrees(z)
    ]


    return pos, rot



def convert(item):

    cls = item.attrib.get(
        "class",
        ""
    )

    props = item.find("Properties")


    if props is not None:

        props = list(props)

        if cls in [
            "Part",
            "MeshPart",
            "TrussPart",
            "WedgePart",
            "CornerWedgePart"
        ]:

            cf = prop(props, "CFrame")
            size = prop(props, "Size")
            col = prop(props, "Color3uint8")
            trans = prop(props, "Transparency")
            name = prop(props, "Name")


            pos, rot = cframe(cf)


            parts.append({
                "T": value(name, cls),
                "P": pos,
                "S": vec(size),
                "R": rot,
                "C": color(col),
                "Tr": float(value(trans, 0))
            })


    for child in item.findall("Item"):
        convert(child)



tree = ET.parse(inp)
root = tree.getroot()


for item in root.findall("Item"):
    convert(item)



with open(out, "w") as f:
    json.dump(
        parts,
        f,
        indent=2
    )


print(
    f"Converted {len(parts)} objects"
)