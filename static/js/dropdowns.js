$(document).ready(() => {
    console.log("Document is ready.");

    // Initializing Select2 Dropdown
    $('.searchable-dropdown').select2({
        dropdownParent: $('.content') // Adjust as needed
    });

    // Load competitions on page load
    $.get('/api/competitions', function (data) {
        const competitions = [...new Set(data.map(d => d.competition_name))];
        competitions.forEach(name => {
            $('#competition-select').append(
                `<option value="${name}">${name}</option>`
            );
        });
        console.log("Loaded competitions into dropdown.");
    }).fail(error => {
        console.error("Error fetching competitions:", error);
    });

    // Populate seasons when competition is selected
    $('#competition-select').on('change', function () {
        const selectedCompetition = $(this).val();

        $('#season-select').empty().append('<option>Select season</option>');

        $.get('/api/competitions', function (data) {
            // Filter the data by competition and populate seasons
            const filtered = data.filter(d => d.competition_name === selectedCompetition);
            filtered.forEach(entry => {
                $('#season-select').append(
                    `<option value="${entry.competition_id}_${entry.season_id}">${entry.season_name}</option>`
                );
            });
            console.log("Loaded seasons into dropdown.");
        }).fail(error => {
            console.error("Error fetching seasons:", error);
        });
    });

    // Populate matches when a season is selected
    $('#season-select').on('change', function () {
        const [competition_id, season_id] = $(this).val().split('_');

        $('#match-select').empty().append('<option>Select match</option>');

        $.get(`/api/matches/${competition_id}/${season_id}`, function (matches) {
            matches.forEach(match => {
                $('#match-select').append(
                    `<option value="${match.match_id}">${match.home_team} vs ${match.away_team}</option>`
                );
            });
            console.log("Loaded matches into dropdown.");
        }).fail(error => {
            console.error("Error fetching matches:", error);
        });
    });
});