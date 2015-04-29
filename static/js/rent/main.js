
var get_list = function(){
	var date = $('#input-date').data('date');
	var classroom_id = $('li[role="presentation"].active').attr('classroom-id');
	$('#loading_img').show();
	$.ajax({
		url: '/ajax/rent/get_content/',
		type: 'post',
		data: {
			date: date,
			classroom_id: classroom_id,
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			$('#loading_img').hide();
			$('#content').html(rsp);
			$('[data-toggle="tooltip"]').tooltip();
		}
	});
};

$(function(){
	$('#input-date').datetimepicker({
		dayViewHeaderFormat: 'YYYY년 MMMM',
		daysOfWeekDisabled: [0, 6],
		minDate: min_date,
		maxDate: max_date,
		showTodayButton: true,
		inline: true,
		format: 'YYYY/MM/DD',
		sideBySide: false
	}).on('dp.change', function(ev){
		get_list();
	});
	get_list();
});

$('li[role="presentation"] a').click(function(){
	$('li[role="presentation"].active').removeClass('active');
	$(this).parent().addClass("active");
	get_list();
});

var delete_rentinfo = function(rentinfo_id){
	$.ajax({
		url: '/ajax/rent/get_rentinfo/',
		type: 'post',
		data: {
			rentinfo_id: rentinfo_id,
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			$('.classroom_name').html(rsp.classroom);
			$('.rent_date').html(rsp.date);
			$('.rent_reason').html(rsp.reason);
			$('.rent_user').html(rsp.name);
			$('.rent_hour').html(rsp.hour+(rsp.classroom_type == 1 ? '교시' : '시'));
			$('#confirmModal [role="delete"]').attr('rentinfo-id', rentinfo_id);
			$('#confirmModal').modal();
		}
	});
};

var write_rentinfo = function(rentinfo_id, hour, hour_text){
	var date = $('#input-date').data('date');
	var classroom_id = $('li[role="presentation"].active').attr('classroom-id');
	var classroom_name = $('li[role="presentation"].active a').html();
	$('#inputDate').val(date);
	$('#inputClassroom').val(classroom_name);
	$('#inputHour').val(hour_text);
	$('#inputReason').val('');
	if (rentinfo_id != 0){ // 수정
		$('#rentModal [role="write"]').html('수정');
		$.ajax({
			url: '/ajax/rent/get_rentinfo/',
			type: 'post',
			data: {
				rentinfo_id: rentinfo_id,
				csrfmiddlewaretoken: csrf_token
			},
			success: function(rsp){
				$('#inputReason').val(rsp.reason);
			}
		});
	}
	else{ // 새로 대관하기
		$('#rentModal [role="write"]').html('작성');
	}
	$('#rentModal [role="write"]').attr('rentinfo-id', rentinfo_id);
	$('#rentModal [role="write"]').attr('date', date);
	$('#rentModal [role="write"]').attr('classroom-id', classroom_id);
	$('#rentModal [role="write"]').attr('hour', hour);
	$('#rentModal').modal();
}

$('#confirmModal [role="delete"]').click(function(){
	$.ajax({
		url: '/ajax/rent/delete_rentinfo/',
		type: 'post',
		data: {
			rentinfo_id: $(this).attr('rentinfo-id'),
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			if (rsp != 'yes') return false;
			$('#confirmModal').modal('hide');
			get_list();
		}
	});
});

$('#rentModal [role="write"]').click(function(){
	var rentinfo_id = $('#rentModal [role="write"]').attr('rentinfo-id');
	var date = $('#rentModal [role="write"]').attr('date');
	var classroom_id = $('#rentModal [role="write"]').attr('classroom-id');
	var hour = $('#rentModal [role="write"]').attr('hour');
	var reason = $('#inputReason').val();
	$.ajax({
		url: '/ajax/rent/write_rentinfo/',
		type: 'post',
		data: {
			rentinfo_id: rentinfo_id,
			date: date,
			classroom_id: classroom_id,
			hour: hour,
			reason: reason,
			csrfmiddlewaretoken: csrf_token
		},
		success: function(rsp){
			if (rsp != 'yes') return false;
			$('#rentModal').modal('hide');
			get_list();
		}
	});
});