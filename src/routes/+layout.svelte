<script>
	import '../app.css';
	let { children } = $props();
</script>

<nav class="sticky top-0 z-50 h-[48px] border-b border-borderDefault bg-pageBg/80 backdrop-blur-md px-6 flex items-center justify-between">
	<div class="flex items-center gap-8 max-w-[1080px] mx-auto w-full">
		<div class="text-primaryText font-semibold text-[15px] tracking-tight flex items-center gap-2 leading-none mt-[2px]">
			<img src="/favicon.png?v=2" alt="WillItRun Logo" class="w-5 h-5 rounded-sm object-contain" />
			WillItRun
		</div>
	</div>
</nav>

<main class="max-w-[1080px] mx-auto pt-12 pb-24 px-6 flex flex-col md:flex-row gap-6">
	{@render children()}
</main>