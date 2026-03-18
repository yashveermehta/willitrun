<script>
	import modelData from '../data/models.json';

	let { 
		userVram = null, 
		userBandwidth = null,
		systemRamGb = null,
		minContextK = null,
		minTokPerSec = null
	} = $props();

	let models = modelData;
	let showTight = $state(false);
	let showNoFit = $state(false);

	let results = $derived((() => {
		const well = [];
		const tight = [];
		const noFit = [];

		const vram = userVram;
		const bandwidth = userBandwidth;
		
		if (!vram) return { well, tight, noFit };

		const effectiveVram = (vram || 0) + ((systemRamGb || 0) * 0.5);

		for (const model of models) {
			const availableForKV = effectiveVram - model.weight_gb;
			
			let maxContextK = 0;
			if (availableForKV > 0) {
				maxContextK = Math.floor(availableForKV / model.kv_per_1k_gb);
				maxContextK = Math.min(maxContextK, model.max_context_k);
			}

			let tokPerSec = null;
			if (bandwidth) {
				tokPerSec = Math.round(bandwidth / (model.weight_gb + 1.0));
			}

			const result = { ...model, maxContextK, tokPerSec };

			if (availableForKV <= 0 || maxContextK <= 0) {
				noFit.push(result);
			} else {
				const meetsContext = minContextK === null || maxContextK >= minContextK;
				const meetsSpeed = minTokPerSec === null || (tokPerSec !== null ? tokPerSec >= minTokPerSec : true);

				if (maxContextK >= 4 && meetsContext && meetsSpeed) {
					well.push(result);
				} else {
					tight.push(result);
				}
			}
		}

		well.sort((a, b) => b.weight_gb - a.weight_gb);
		tight.sort((a, b) => b.weight_gb - a.weight_gb);
		noFit.sort((a, b) => b.weight_gb - a.weight_gb);

		return { well, tight, noFit };
	})());
</script>

<section class="flex-grow">
	{#if !userVram}
		<div class="bg-cardSurface border border-borderDefault rounded-[12px] p-16 text-center h-full flex flex-col justify-center shadow-lg">
			<h2 class="text-primaryText text-2xl font-bold mb-4">Select Hardware Configuration</h2>
			<p class="text-secondaryText text-sm max-w-sm mx-auto">Pick a GPU accelerator or enter your VRAM specifications on the left to instantly estimate model performance and compatibility.</p>
		</div>
	{:else}
		<div class="flex items-center flex-wrap gap-3 mb-10">
			<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-elevated border border-borderDefault">
				<span class="w-1.5 h-1.5 rounded-full bg-accentGreen shadow-[0_0_8px_rgba(29,185,84,0.4)]"></span>
				<span class="text-[12px] text-primaryText">{results.well.length} runs well</span>
			</div>
			<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-elevated border border-borderDefault">
				<span class="w-1.5 h-1.5 rounded-full bg-accentAmber shadow-[0_0_8px_rgba(240,164,41,0.4)]"></span>
				<span class="text-[12px] text-primaryText">{results.tight.length} tight fit</span>
			</div>
			<div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-elevated border border-borderDefault">
				<span class="w-1.5 h-1.5 rounded-full bg-tertiaryText"></span>
				<span class="text-[12px] text-secondaryText">{results.noFit.length} won't fit</span>
			</div>
		</div>

		<div class="space-y-12">
			{#if results.well.length > 0}
				<div>
					<h2 class="text-[11px] font-semibold text-accentGreen tracking-[0.15em] uppercase mb-4 px-1">RUNS WELL — {results.well.length} MODELS</h2>
					<div class="flex flex-col gap-[6px]">
						{#each results.well as model}
							<div class="model-card-hover bg-cardSurface border border-borderDefault rounded-[10px] p-4 flex gap-4 transition-all duration-200 relative overflow-hidden group">
								<div class="absolute left-0 top-0 bottom-0 w-[3px] bg-accentGreen shadow-[2px_0_8px_rgba(29,185,84,0.2)]"></div>
								<div class="flex flex-col flex-grow">
									<div class="flex items-center justify-between mb-3">
										<div class="flex items-center gap-3">
											<span class="text-[14px] font-medium text-primaryText">{model.name}</span>
											<span class="bg-accentViolet/10 text-accentViolet text-[10px] px-1.5 py-0.5 rounded font-medium border border-accentViolet/20">{model.quantization}</span>
										</div>
										<span class="text-tertiaryText text-[11px] whitespace-nowrap ml-2">{model.weight_gb.toFixed(1)} GB vRAM</span>
									</div>
									<div class="flex items-center gap-4 sm:gap-6 flex-wrap">
										<div class="flex items-center gap-1.5">
											<svg class="w-3.5 h-3.5 text-secondaryText" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
											<span class="text-[12px] text-secondaryText">{model.weight_gb.toFixed(2)} GB Weights</span>
										</div>
										<div class="flex items-center gap-1.5">
											<svg class="w-3.5 h-3.5 text-secondaryText" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
											<span class="text-[12px] text-secondaryText">{model.maxContextK.toLocaleString()}K Max Ctx</span>
										</div>
										{#if model.tokPerSec}
											<div class="flex items-center gap-1.5">
												<svg class="w-3.5 h-3.5 text-accentGreen" fill="currentColor" viewBox="0 0 24 24"><path d="M13 10V3L4 14H11V21L20 10H13Z"></path></svg>
												<span class="text-[12px] text-primaryText font-medium">{model.tokPerSec} tok/s</span>
											</div>
										{/if}
									</div>
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			{#if results.tight.length > 0}
				<div>
					<button class="w-full flex items-center gap-3 text-left focus:outline-none group mb-4" onclick={() => showTight = !showTight}>
						<h2 class="text-[11px] font-semibold text-accentAmber tracking-[0.15em] uppercase px-1 m-0">TIGHT FIT — {results.tight.length} MODELS</h2>
						<svg class="w-4 h-4 text-accentAmber transition-transform duration-200 {showTight ? 'rotate-180': ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
					</button>
					{#if showTight}
						<div class="flex flex-col gap-[6px] slide-down">
							{#each results.tight as model}
								<div class="model-card-hover bg-cardSurface border border-borderDefault rounded-[10px] p-4 flex gap-4 transition-all duration-200 relative overflow-hidden group">
									<div class="absolute left-0 top-0 bottom-0 w-[3px] bg-accentAmber shadow-[2px_0_8px_rgba(240,164,41,0.2)]"></div>
									<div class="flex flex-col flex-grow">
										<div class="flex items-center justify-between mb-3">
											<div class="flex items-center gap-3">
												<span class="text-[14px] font-medium text-primaryText">{model.name}</span>
												<span class="bg-accentViolet/10 text-accentViolet text-[10px] px-1.5 py-0.5 rounded font-medium border border-accentViolet/20">{model.quantization}</span>
											</div>
											<span class="text-tertiaryText text-[11px] whitespace-nowrap ml-2">{model.weight_gb.toFixed(1)} GB vRAM</span>
										</div>
										<div class="flex items-center gap-4 sm:gap-6 flex-wrap">
											<div class="flex items-center gap-1.5">
												<svg class="w-3.5 h-3.5 text-secondaryText" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
												<span class="text-[12px] text-secondaryText">{model.weight_gb.toFixed(2)} GB Weights</span>
											</div>
											<div class="flex items-center gap-1.5">
												<svg class="w-3.5 h-3.5 text-secondaryText" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
												<span class="text-[12px] text-secondaryText">{model.maxContextK.toLocaleString()}K Max Ctx</span>
											</div>
											{#if model.tokPerSec}
												<div class="flex items-center gap-1.5">
													<svg class="w-3.5 h-3.5 text-accentAmber" fill="currentColor" viewBox="0 0 24 24"><path d="M13 10V3L4 14H11V21L20 10H13Z"></path></svg>
													<span class="text-[12px] text-primaryText font-medium">{model.tokPerSec} tok/s</span>
												</div>
											{/if}
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}

			{#if results.noFit.length > 0}
				<div class="opacity-50">
					<button class="w-full flex items-center gap-3 text-left focus:outline-none group mb-4" onclick={() => showNoFit = !showNoFit}>
						<h2 class="text-[11px] font-semibold text-tertiaryText tracking-[0.15em] uppercase px-1 m-0">INCOMPATIBLE — {results.noFit.length} MODELS</h2>
						<svg class="w-4 h-4 text-tertiaryText transition-transform duration-200 {showNoFit ? 'rotate-180': ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
					</button>
					{#if showNoFit}
						<div class="flex flex-col gap-[6px] slide-down">
							{#each results.noFit as model}
								<div class="bg-cardSurface border border-borderDefault rounded-[10px] p-4 flex gap-4 transition-all duration-200 relative overflow-hidden group">
									<div class="absolute left-0 top-0 bottom-0 w-[3px] bg-tertiaryText"></div>
									<div class="flex flex-col flex-grow">
										<div class="flex items-center justify-between mb-3">
											<div class="flex items-center gap-3">
												<span class="text-[14px] font-medium text-primaryText">{model.name}</span>
												<span class="bg-tertiaryText/10 text-tertiaryText text-[10px] px-1.5 py-0.5 rounded font-medium border border-tertiaryText/20">{model.quantization}</span>
											</div>
											<span class="text-tertiaryText text-[11px] whitespace-nowrap ml-2">{model.weight_gb.toFixed(1)} GB vRAM</span>
										</div>
										<div class="flex items-center gap-4 sm:gap-6 flex-wrap">
											<div class="flex items-center gap-1.5">
												<svg class="w-3.5 h-3.5 text-tertiaryText" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
												<span class="text-[12px] text-tertiaryText">{model.weight_gb.toFixed(2)} GB Weights</span>
											</div>
											<div class="flex items-center gap-1.5 text-accentAmber">
												<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
												<span class="text-[12px]">Insufficient vRAM</span>
											</div>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</section>
