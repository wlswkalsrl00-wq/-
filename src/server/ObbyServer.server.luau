-- 점프맵 서버 스크립트: 체크포인트, 사망 처리, 사라지는 발판, 완주/재시작
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")

local checkpoints: { [number]: BasePart } = {}

local function onTagged(tag: string, callback: (BasePart) -> ())
	for _, inst in CollectionService:GetTagged(tag) do
		if inst:IsA("BasePart") then
			task.spawn(callback, inst)
		end
	end
	CollectionService:GetInstanceAddedSignal(tag):Connect(function(inst)
		if inst:IsA("BasePart") then
			callback(inst)
		end
	end)
end

local function playerFromHit(hit: BasePart): (Player?, Humanoid?)
	local character = hit.Parent
	if not character then
		return nil, nil
	end
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if not humanoid or humanoid.Health <= 0 then
		return nil, nil
	end
	return Players:GetPlayerFromCharacter(character), humanoid
end

local function getStageValue(player: Player): IntValue?
	local stats = player:FindFirstChild("leaderstats")
	local stage = stats and stats:FindFirstChild("Stage")
	if stage and stage:IsA("IntValue") then
		return stage
	end
	return nil
end

-- 닿으면 죽는 파트
onTagged("KillBrick", function(part)
	part.Touched:Connect(function(hit)
		local _, humanoid = playerFromHit(hit)
		if humanoid then
			humanoid.Health = 0
		end
	end)
end)

-- 체크포인트: 더 높은 단계에 닿으면 저장
onTagged("Checkpoint", function(part)
	local stageNumber = part:GetAttribute("Stage")
	if typeof(stageNumber) ~= "number" then
		return
	end
	checkpoints[stageNumber] = part
	local isFinish = CollectionService:HasTag(part, "Finish")

	part.Touched:Connect(function(hit)
		local player, humanoid = playerFromHit(hit)
		if not player or not humanoid then
			return
		end
		local stage = getStageValue(player)
		if not stage or stage.Value >= stageNumber then
			return
		end
		stage.Value = stageNumber

		if isFinish then
			local root = humanoid.RootPart
			if root and not root:FindFirstChild("FinishSparkles") then
				local sparkles = Instance.new("Sparkles")
				sparkles.Name = "FinishSparkles"
				sparkles.Parent = root
			end
		end
	end)
end)

-- 사라지는 발판: 밟으면 잠시 뒤 사라졌다가 다시 나타남
onTagged("Vanish", function(part)
	local baseTransparency = part.Transparency
	local busy = false
	part.Touched:Connect(function(hit)
		if busy then
			return
		end
		local _, humanoid = playerFromHit(hit)
		if not humanoid then
			return
		end
		busy = true
		local fade = TweenService:Create(part, TweenInfo.new(0.7), { Transparency = 1 })
		fade:Play()
		fade.Completed:Wait()
		part.CanCollide = false
		task.wait(2.5)
		part.Transparency = baseTransparency
		part.CanCollide = true
		busy = false
	end)
end)

-- 처음부터 다시
onTagged("Restart", function(part)
	local cooldown: { [Player]: boolean } = {}
	part.Touched:Connect(function(hit)
		local player = playerFromHit(hit)
		if not player or cooldown[player] then
			return
		end
		local stage = getStageValue(player)
		if not stage then
			return
		end
		cooldown[player] = true
		stage.Value = 0
		player:LoadCharacter()
		task.wait(1)
		cooldown[player] = nil
	end)
end)

local function onCharacterAdded(player: Player, character: Model)
	local stage = getStageValue(player)
	local checkpoint = stage and checkpoints[stage.Value]
	if not checkpoint then
		return -- 0단계: 기본 스폰 위치 사용
	end
	character:WaitForChild("HumanoidRootPart")
	task.wait() -- 기본 스폰 배치가 끝난 뒤 옮긴다
	character:PivotTo(checkpoint.CFrame + Vector3.new(0, 5, 0))
end

local function onPlayerAdded(player: Player)
	local stats = Instance.new("Folder")
	stats.Name = "leaderstats"
	local stage = Instance.new("IntValue")
	stage.Name = "Stage"
	stage.Parent = stats
	stats.Parent = player

	player.CharacterAdded:Connect(function(character)
		onCharacterAdded(player, character)
	end)
	if player.Character then
		onCharacterAdded(player, player.Character)
	end
end

Players.PlayerAdded:Connect(onPlayerAdded)
for _, player in Players:GetPlayers() do
	task.spawn(onPlayerAdded, player)
end
