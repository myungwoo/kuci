

$(function(){
	$('#input-date').datetimepicker({
		daysOfWeekDisabled: [0, 6],
		minDate: new Date(),
		showTodayButton: true,
		inline: true,
		format: 'YYYY/MM/DD',
		sideBySide: false
	}).on('dp.change', function(ev){
		alert($(this).data('date'));
	});
});