-- 점프맵 클라이언트 스크립트: 움직이는 발판과 회전 막대를 부드럽게 움직인다.
-- 서버 시각을 기준으로 계산하므로 모든 플레이어 화면에서 같은 위치에 보인다.
local CollectionService = game:GetService("CollectionService")
local RunService = game:GetService("RunService")

type Mover = { origin: CFrame, offset: Vector3, speed: number, phase: number }
type Spinner = { origin: CFrame, speed: number }

local movers: { [BasePart]: Mover } = {}
local spinners: { [BasePart]: Spinner } = {}

local function track(tag: string, added: (BasePart) -> (), removed: (BasePart) -> ())
	for _, inst in CollectionService:GetTagged(tag) do
		if inst:IsA("BasePart") then
			added(inst)
		end
	end
	CollectionService:GetInstanceAddedSignal(tag):Connect(function(inst)
		if inst:IsA("BasePart") then
			added(inst)
		end
	end)
	CollectionService:GetInstanceRemovedSignal(tag):Connect(function(inst)
		if inst:IsA("BasePart") then
			removed(inst)
		end
	end)
end

local function numberAttribute(part: BasePart, name: string, default: number): number
	local value = part:GetAttribute(name)
	return if typeof(value) == "number" then value else default
end

track("Mover", function(part)
	local offset = part:GetAttribute("MoveOffset")
	if typeof(offset) ~= "Vector3" then
		return
	end
	local period = math.max(numberAttribute(part, "Period", 5), 0.5)
	movers[part] = {
		origin = part.CFrame,
		offset = offset,
		speed = 2 * math.pi / period,
		phase = numberAttribute(part, "Phase", 0),
	}
end, function(part)
	movers[part] = nil
end)

track("Spinner", function(part)
	spinners[part] = {
		origin = part.CFrame,
		speed = numberAttribute(part, "SpinSpeed", 1.5),
	}
end, function(part)
	spinners[part] = nil
end)

RunService.PreSimulation:Connect(function()
	local now = workspace:GetServerTimeNow()

	for part, mover in movers do
		local angle = (now * mover.speed + mover.phase) % (2 * math.pi)
		local alpha = 0.5 - 0.5 * math.cos(angle)
		part.CFrame = mover.origin + mover.offset * alpha
		-- 속도를 넣어 줘야 위에 선 캐릭터가 발판을 따라 움직인다.
		part.AssemblyLinearVelocity = mover.offset * (0.5 * mover.speed * math.sin(angle))
	end

	for part, spinner in spinners do
		local angle = (now * spinner.speed) % (2 * math.pi)
		part.CFrame = spinner.origin * CFrame.Angles(0, angle, 0)
	end
end)
