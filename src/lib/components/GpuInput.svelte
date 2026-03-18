<script>
	import SearchSelect from './SearchSelect.svelte';
	import gpuData from '../data/gpus.json';

	let { 
		userVram = $bindable(null), 
		userBandwidth = $bindable(null),
		systemRamGb = $bindable(null),
		minContextK = $bindable(null),
		minTokPerSec = $bindable(null)
	} = $props();

	let gpus = gpuData;
	let selectedGpuId = $state(null);
	let manualVram = $state('');
	let selectedVramOption = $state(null);

	$effect(() => {
		if (selectedGpuId) {
			const gpu = gpus.find(g => g.id === selectedGpuId);
			manualVram = ''; 
			if (gpu) {
				if (gpu.vram_options) {
					if (!selectedVramOption || !gpu.vram_options.some(o => o.vram_gb === selectedVramOption)) {
						selectedVramOption = gpu.vram_options[0].vram_gb;
					}
					const opt = gpu.vram_options.find(o => o.vram_gb === selectedVramOption);
					userVram = opt ? opt.vram_gb : null;
					userBandwidth = opt ? opt.bandwidth_gbps : null;
				} else {
					selectedVramOption = null;
					userVram = gpu.vram_gb;
					userBandwidth = gpu.bandwidth_gbps;
				}
			}
		} else {
			selectedVramOption = null;
			userBandwidth = null;
			userVram = manualVram ? Number(manualVram) : null;
		}
	});

	function handleManualVramChange() {
		selectedGpuId = null;
		userVram = manualVram ? Number(manualVram) : null;
	}
</script>

<aside class="w-full md:w-[360px] flex-shrink-0">
	<div class="bg-cardSurface border border-borderDefault rounded-[12px] p-6 inner-top-highlight flex flex-col gap-8 sticky top-20">
		<section>
			<label class="text-[10px] font-semibold text-accentViolet tracking-[0.15em] mb-4 block">YOUR HARDWARE</label>
			<div class="space-y-5">
				<div>
					<label class="text-[11px] text-tertiaryText tracking-widest block mb-2 uppercase">GPU ACCELERATOR</label>
					<SearchSelect 
						options={gpus} 
						bind:value={selectedGpuId} 
						placeholder="Search GPUs..." 
						groupBy="manufacturer"
					/>
				</div>

				{#if selectedGpuId && gpus.find(g => g.id === selectedGpuId)?.vram_options}
					<div class="slide-down">
						<label class="text-[11px] text-tertiaryText tracking-widest block mb-2 uppercase">CHIP MEMORY CONFIG</label>
						<div class="relative">
							<select class="w-full bg-elevated border border-borderDefault rounded-md px-3 py-2 text-[13px] text-primaryText appearance-none focus:ring-1 focus:ring-accentViolet outline-none" bind:value={selectedVramOption}>
								{#each gpus.find(g => g.id === selectedGpuId).vram_options as opt}
									<option value={opt.vram_gb}>{opt.vram_gb} GB Unified Memory</option>
								{/each}
							</select>
							<div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-tertiaryText">
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
							</div>
						</div>
					</div>
				{/if}

				<div>
					<label class="text-[11px] text-tertiaryText tracking-widest block mb-2 uppercase">DEDICATED VRAM (OR MANUAL)</label>
					<div class="flex items-center bg-elevated border border-borderDefault rounded-md px-3 py-2 focus-within:ring-1 focus-within:ring-accentViolet transition-colors">
						<input 
							class="bg-transparent border-none p-0 text-[13px] text-primaryText focus:ring-0 w-full outline-none" 
							type="number" 
							placeholder="e.g. 24"
							bind:value={manualVram} 
							oninput={handleManualVramChange}
						/>
						<span class="text-[11px] text-tertiaryText font-medium ml-2">GB</span>
					</div>
				</div>
                
				<div>
					<label class="text-[11px] text-tertiaryText tracking-widest block mb-2 uppercase">SYSTEM RAM FOR OFFLOAD</label>
					<div class="flex items-center bg-elevated border border-borderDefault rounded-md px-3 py-2 focus-within:ring-1 focus-within:ring-accentViolet transition-colors">
						<input 
							class="bg-transparent border-none p-0 text-[13px] text-primaryText focus:ring-0 w-full outline-none" 
							type="number" 
							placeholder="e.g. 64"
							bind:value={systemRamGb}
						/>
						<span class="text-[11px] text-tertiaryText font-medium ml-2">GB</span>
					</div>
				</div>
			</div>
		</section>

		<section class="border-t border-borderDefault pt-6">
			<label class="text-[10px] font-semibold text-accentViolet tracking-[0.15em] mb-4 block">INFERENCE CONTEXT</label>
			<div class="space-y-4">
				<div>
					<label class="text-[11px] text-tertiaryText tracking-widest block mb-2 uppercase">CONTEXT WINDOW</label>
					<div class="relative">
						<select class="w-full bg-elevated border border-borderDefault rounded-md px-3 py-2 text-[13px] text-primaryText appearance-none focus:ring-1 focus:ring-accentViolet outline-none transition-colors" bind:value={minContextK}>
							<option value={null}>Any Context Size</option>
							<option value={4}>4,096 (Standard)</option>
							<option value={8}>8,192 (Medium)</option>
							<option value={32}>32,768 (Long)</option>
							<option value={128}>131,072 (Massive)</option>
						</select>
						<div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-tertiaryText">
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
						</div>
					</div>
				</div>
				<div>
					<label class="text-[11px] text-tertiaryText tracking-widest block mb-2 uppercase">MIN. THROUGHPUT</label>
					<div class="relative">
						<select class="w-full bg-elevated border border-borderDefault rounded-md px-3 py-2 text-[13px] text-primaryText appearance-none focus:ring-1 focus:ring-accentViolet outline-none transition-colors" bind:value={minTokPerSec}>
							<option value={null}>No Preference</option>
							<option value={10}>&gt; 10 tok/s</option>
							<option value={30}>&gt; 30 tok/s</option>
							<option value={50}>&gt; 50 tok/s</option>
							<option value={100}>&gt; 100 tok/s</option>
						</select>
						<div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-tertiaryText">
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
						</div>
					</div>
				</div>
			</div>
		</section>

		<div class="pt-6 border-t border-borderDefault">
			<div class="text-[11px] text-secondaryText leading-relaxed">
				Estimates are based on the selected quantization limits using empirical vRAM overhead.
			</div>
		</div>
	</div>
</aside>
