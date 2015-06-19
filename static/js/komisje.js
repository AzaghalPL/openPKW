/****************** Zabezpieczenie przed CSRF ******************/

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


/****************** Event handlers ******************/

$(document).ready(function() {

/* czyszczenie komunikatów o błędach */
	$('a#errors_clear').click( function(event) {
		event.preventDefault();
		$('ul#errors_list').empty();
	});

/* rozpoczęcie edycji wiersza */
	$('table#komisje').on( 'click', 'a.edit', function(event) {
		event.preventDefault();
		var row = $(this).parent().parent();
		$.get( './data', { id: row.attr('id') }, function (json) {			
			row.addClass('editing');
			row.append('<input type="hidden" name="version" value="' + json.version + '">');
			row.children(':not(.name)').empty();
			row.children('.cards').append('<input name="cards" type="text" value="' + json.cards + '">');
			row.children('.population').append('<input name="population" type="text" value="' + json.population + '">');
			row.children('.buttons').append('<a class="save" href=".">zapisz</a><br><a class="cancel" href=".">anuluj</a>');
		}); // jak się nie uda to i tak trzeba spróbować jeszcze raz
	});

/* anulowanie edycji wiersza */
	$('table#komisje').on( 'click', 'a.cancel', function(event) {
		event.preventDefault();
		var row = $(this).parent().parent();
		$.get( './data', { id: row.attr('id') }, function (json) {
			row.children('input[type="hidden"]').remove();			
			row.children(':not(.name)').empty();
			row.children('.cards').append(json.cards);
			row.children('.population').append(json.population);
			row.children().removeClass('invalid');
			row.removeClass('editing');
		}); // jak się nie uda to i tak trzeba próbować ponownie
	});

/* zapisanie wartości po edycji wiersza */
	$('table#komisje').on( 'click', 'a.save', function(event) {
		event.preventDefault();
		var row = $(this).parent().parent();
		$.post( './update', {
			id: row.attr('id'),
			cards: row.children('.cards').children('input').val(),
			population: row.children('.population').children('input').val(),
			version: row.children('input[name="version"]').val()},
		function (json) {
			row.children('input[type="hidden"]').remove();
			row.children(':not(.name)').empty();
			row.children('.cards').append(json.cards);
			row.children('.population').append(json.population);
			row.children().removeClass('invalid');
			row.removeClass('editing');
		})
		.error( function(xhr) {
			json = xhr.responseJSON;
			row.children().removeClass('invalid');
			if (xhr.status === 409) {
			// 409 = konflikt z bazą danych
				row.children('input[name="version"]').val(json.version);
				row.find('input[name="cards"]').val(json.cards);
				row.find('input[name="population"]').val(json.population);
				$('ul#errors_list').append('<li>Dane zostały zmienione przez innego użytkownika.</li>');
			} else if (xhr.status === 400) {
			// 400 = błąd walidacji
				if (json.cards) {
					row.children('.cards').addClass('invalid');
				}
				if (json.population) {
					row.children('.population').addClass('invalid');
				}
				$('ul#errors_list').append('<li>Proszę wprowadzić dodatnie liczby całkowite.</li>');
			}
		})
	});

/* link do edycji po najechaniu myszką na wiersz */
        $('table#komisje').hoverIntent({
	over: function() {
		$(this).children('.buttons').append('<a class="edit" href=".">wprowadź frekwencję</a>').hide();
		$(this).children('.buttons').fadeIn(700);
		$(this).children().addClass('.highlighted');
	},
	out: function() {
		$(this).children().removeClass('.highlighted');
		$(this).children('.buttons').fadeOut(700, function() {
        		$(this).empty();
		});
	},
	selector: 'tr:not(.editing, .table_header)',
	interval: 500});

});
