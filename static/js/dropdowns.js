$(document).ready(function () {
    $('.searchable-dropdown').select2(
        {
            dropdownParent: $('.content') // or a direct visible wrapper
        }
    );


    // Load competitions/seasons on page load
    $.get('/api/competitions', function (data) {
        const competitions = [...new Set(data.map(d => d.competition_name))];
        $('#competition-select').append(
            competitions.map(name => `<option value="${name}">${name}</option>`)
        );
    });

    // Populate seasons based on competition
    $('#competition-select').on('change', function () {
        const selectedCompetition = $(this).val();
        $('#season-select').empty().append('<option>Select season</option>');

        $.get('/api/competitions', function (data) {
            const filtered = data.filter(d => d.competition_name === selectedCompetition);
            filtered.forEach(entry => {
                $('#season-select').append(
                    `<option value="${entry.competition_id}_${entry.season_id}">${entry.season_name}</option>`
                );
            });
        });
    });

    // Populate matches based on competition_id + season_id
    $('#season-select').on('change', function () {
        const [competition_id, season_id] = $(this).val().split('_');

        $('#match-select').empty().append('<option>Select match</option>');

        $.get(`/api/matches/${competition_id}/${season_id}`, function (matches) {
            matches.forEach(m => {
                $('#match-select').append(
                    `<option value="${m.match_id}">${m.home_team} vs ${m.away_team}</option>`
                );
            });
        });
    });

    // Get match event data
    $('#match-select').on('change', function () {
        const matchId = $(this).val();
        $.get(`/api/events/${matchId}`, function (eventData) {
            console.log("Event data for match:", eventData);
            // Add your rendering logic here
        });
    });
});
