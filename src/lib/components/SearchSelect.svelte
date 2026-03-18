<script>
	let { 
		options = [], 
		value = $bindable(), 
		placeholder = "Select...", 
		labelKey = "name", 
		valueKey = "id",
		groupBy = null 
	} = $props();

	let isOpen = $state(false);
	let searchTerm = $state('');
	let selectContainer;

	let filteredOptions = $derived(
		options.filter(opt => 
			opt[labelKey].toLowerCase().includes(searchTerm.toLowerCase())
		)
	);

	let groupedOptions = $derived(
		(() => {
			if (!groupBy) return { "": filteredOptions };
			const groups = {};
			for (const opt of filteredOptions) {
				const group = opt[groupBy] || "Other";
				if (!groups[group]) groups[group] = [];
				groups[group].push(opt);
			}
			return groups;
		})()
	);

	function handleInput(e) {
		searchTerm = e.target.value;
		isOpen = true;
	}

	function selectOption(opt) {
		value = opt[valueKey];
		searchTerm = opt[labelKey];
		isOpen = false;
	}

	function handleBlur(e) {
		if (!selectContainer.contains(e.relatedTarget)) {
			isOpen = false;
			const selected = options.find(o => o[valueKey] === value);
			searchTerm = selected ? selected[labelKey] : '';
		}
	}

	$effect(() => {
		const selected = options.find(o => o[valueKey] === value);
		if (!isOpen) {
			searchTerm = selected ? selected[labelKey] : (value ? '' : '');
		}
	});
</script>

<div class="relative" bind:this={selectContainer} onfocusout={handleBlur}>
	<input
		type="text"
		class="w-full bg-elevated border border-borderDefault rounded-md px-3 py-2 text-[13px] text-primaryText focus:ring-1 focus:ring-accentViolet outline-none transition-colors appearance-none"
		placeholder={placeholder}
		bind:value={searchTerm}
		oninput={handleInput}
		onfocus={() => isOpen = true}
	/>
	<div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-tertiaryText">
		<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
	</div>

	{#if isOpen && filteredOptions.length > 0}
		<div class="absolute z-50 w-full mt-1 bg-elevated border border-borderDefault rounded-md shadow-lg max-h-[300px] overflow-y-auto custom-scrollbar flex flex-col p-1">
			{#if groupBy}
				{#each Object.entries(groupedOptions) as [groupName, opts]}
					{#if opts.length > 0}
						<div class="px-2 py-1.5 text-[10px] font-bold text-accentViolet uppercase tracking-wider mt-1">{groupName}</div>
						{#each opts as opt}
							<button class="w-full text-left px-3 py-2 text-[13px] text-primaryText hover:bg-cardHover rounded-md transition-colors" onclick={() => selectOption(opt)}>
								{opt[labelKey]}
							</button>
						{/each}
					{/if}
				{/each}
			{:else}
				{#each filteredOptions as opt}
					<button class="w-full text-left px-3 py-2 text-[13px] text-primaryText hover:bg-cardHover rounded-md transition-colors" onclick={() => selectOption(opt)}>
						{opt[labelKey]}
					</button>
				{/each}
			{/if}
		</div>
	{/if}
</div>
