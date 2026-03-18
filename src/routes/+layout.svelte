<script>
	import '../app.css';
	let { children } = $props();
</script>

<nav class="sticky top-0 z-50 h-[48px] border-b border-borderDefault bg-pageBg/80 backdrop-blur-md px-6 flex items-center justify-between">
	<div class="flex items-center gap-8 max-w-[1080px] mx-auto w-full">
		<div class="text-primaryText font-semibold text-[15px] tracking-tight flex items-center gap-2 leading-none mt-[2px]">
			<img src="/favicon.png?v=2" alt="WillItRun Logo" class="w-5 h-5 rounded-sm shadow-[0_0_12px_rgba(124,106,247,0.3)] object-contain" />
			WillItRun
		</div>
		<div class="flex items-center gap-6">
			<a class="text-secondaryText hover:text-primaryText text-sm transition-colors" href="/">Models</a>
			<a class="text-secondaryText hover:text-primaryText text-sm transition-colors" href="/compare">Compare</a>
			<a class="text-secondaryText hover:text-primaryText text-sm transition-colors" href="/bench">Bench</a>
		</div>
		<div class="ml-auto">
			<button class="text-secondaryText hover:text-primaryText text-[13px] border border-borderDefault rounded-md px-3 py-1 bg-cardSurface transition-all hover:bg-borderHover hover:text-primaryText">Connect GPU</button>
		</div>
	</div>
</nav>

<main class="max-w-[1080px] mx-auto pt-12 pb-24 px-6 flex flex-col md:flex-row gap-6">
	{@render children()}
</main>

<footer class="max-w-[1080px] mx-auto px-6 py-8 border-t border-borderDefault flex items-center justify-between">
	<div class="text-[11px] text-tertiaryText uppercase tracking-wider">
      Last data sync: Recently
    </div>
	<div class="flex flex-wrap items-center justify-center gap-6">
		<a class="text-[12px] text-secondaryText hover:text-primaryText transition-colors" href="https://huggingface.co/models" target="_blank" rel="noopener noreferrer">HuggingFace API</a>
		<a class="text-[12px] text-secondaryText hover:text-primaryText transition-colors" href="https://github.com/" target="_blank" rel="noopener noreferrer">Open Source</a>
		<a class="text-[12px] text-secondaryText hover:text-primaryText transition-colors" href="/privacy">Privacy</a>
	</div>
</footer>
