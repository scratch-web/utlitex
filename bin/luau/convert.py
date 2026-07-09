import json

def hex_to_rgb(hex_color):
    hex_color = hex_color.strip().lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

with open("model.json", "r") as f:
    parts = json.load(f)

min_x = min(p["P"][0] - p["S"][0] / 2 for p in parts)
max_x = max(p["P"][0] + p["S"][0] / 2 for p in parts)
min_y = min(p["P"][1] - p["S"][1] / 2 for p in parts)
min_z = min(p["P"][2] - p["S"][2] / 2 for p in parts)
max_z = max(p["P"][2] + p["S"][2] / 2 for p in parts)

center_x = (min_x + max_x) / 2
center_z = (min_z + max_z) / 2
offset_y = min_y

lines = [
    'local model = Instance.new("Model")',
    'model.Name = "VortexModel"',
    'model.Parent = workspace',
    '',
    'local parts = {'
]

for p in parts:
    pos = p["P"]
    rot = p["R"]
    size = p["S"]
    r, g, b = hex_to_rgb(p["C"])
    tr = p["Tr"]
    name = p["T"]

    px = pos[0] - center_x
    py = pos[1] - offset_y
    pz = pos[2] - center_z

    lines.append(
        f'\t{{N = "{name}", P = Vector3.new({px}, {py}, {pz}), '
        f'R = Vector3.new({rot[0]}, {rot[1]}, {rot[2]}), '
        f'S = Vector3.new({size[0]}, {size[1]}, {size[2]}), '
        f'C = Color3.fromRGB({r}, {g}, {b}), '
        f'Tr = {tr}}},'
    )

lines.extend([
    '}',
    '',
    'local center = Instance.new("Part")',
    'center.Name = "Center"',
    'center.Size = Vector3.new(1, 1, 1)',
    'center.Transparency = 1',
    'center.CanCollide = false',
    'center.Anchored = true',
    'center.CFrame = CFrame.new(0, 0, 0)',
    'center.Parent = model',
    '',
    'for _, data in ipairs(parts) do',
    '\tlocal part = Instance.new("Part")',
    '\tpart.Name = data.N',
    '\tpart.Size = data.S',
    '\tpart.CFrame = CFrame.new(data.P) * CFrame.Angles(',
    '\t\tmath.rad(data.R.X),',
    '\t\tmath.rad(data.R.Y),',
    '\t\tmath.rad(data.R.Z)',
    '\t)',
    '\tpart.Color = data.C',
    '\tpart.Transparency = data.Tr',
    '\tpart.Material = Enum.Material.SmoothPlastic',
    '\tpart.Anchored = true',
    '\tpart.TopSurface = Enum.SurfaceType.Studs',
    '\tpart.BottomSurface = Enum.SurfaceType.Studs',
    '\tpart.LeftSurface = Enum.SurfaceType.Studs',
    '\tpart.RightSurface = Enum.SurfaceType.Studs',
    '\tpart.FrontSurface = Enum.SurfaceType.Studs',
    '\tpart.BackSurface = Enum.SurfaceType.Studs',
    '\tpart.Parent = model',
    'end',
    '',
    'model.PrimaryPart = center',
    'model:SetPrimaryPartCFrame(CFrame.new(0, 0, 0))'
])

with open("output.txt", "w", newline="\n") as f:
    f.write("\n".join(lines))

print("copy output.txt into your roblox studio command bar, then run it for the model")