$(document).ready(() => {
    console.log("Document is ready.");

    // Initialize Select2 for better UX
    $('.searchable-dropdown').select2({
        dropdownParent: $('.content')
    });

    // Fetch and populate competitions on page load
    $.get('/api/competitions', function (data) {
        const uniqueCompetitions = [...new Set(data.map(d => d.competition_name))];
        uniqueCompetitions.forEach(name => {
            $('#competition-select').append(
                `<option value="${name}">${name}</option>`
            );
        });
        console.log("✅ Loaded competitions");
    }).fail(error => {
        console.error("❌ Error fetching competitions:", error);
    });

    // Load seasons when a competition is selected
    $('#competition-select').on('change', function () {
        const selectedCompetition = $(this).val();
        $('#season-select').empty().append('<option>Select season</option>');
        $('#match-select').empty().append('<option>Select match</option>');

        $.get('/api/competitions', function (data) {
            const filtered = data.filter(d => d.competition_name === selectedCompetition);
            filtered.forEach(entry => {
                $('#season-select').append(
                    `<option value="${entry.season_id}">${entry.season_name}</option>`
                );
            });
            console.log("✅ Loaded seasons");
        }).fail(error => {
            console.error("❌ Error fetching seasons:", error);
        });
    });

    // Load matches when a season is selected
    $('#season-select').on('change', function () {
        const season_id = $(this).val();
        $('#match-select').empty().append('<option>Select match</option>');

        $.get(`/api/matches/${season_id}`, function (matches) {
            matches.forEach(match => {
                $('#match-select').append(
                    `<option value="${match.match_id}">${match.home_team} vs ${match.away_team}</option>`
                );
            });
            console.log("✅ Loaded matches");
        }).fail(error => {
            console.error("❌ Error fetching matches:", error);
        });
    });
});
