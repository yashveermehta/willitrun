<script>
	import GpuInput from '../lib/components/GpuInput.svelte';
	import ModelResults from '../lib/components/ModelResults.svelte';

	let userVram = $state(null);
	let userBandwidth = $state(null);
	let minContextK = $state(null);
	let minTokPerSec = $state(null);
	let systemRamGb = $state(null);
</script>

<GpuInput 
	bind:userVram
	bind:userBandwidth
	bind:minContextK
	bind:minTokPerSec
	bind:systemRamGb
/>
<ModelResults 
	{userVram}
	{userBandwidth}
	{minContextK}
	{minTokPerSec}
	{systemRamGb}
/>
