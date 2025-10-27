document.addEventListener('DOMContentLoaded', function () {
    const selectCategorie = document.getElementById('id_categorie');
    const tailleRows = document.querySelectorAll('.form-row.field-taille');

    function normalize(value) {
        return value.trim().toLowerCase();
    }

    function isShoeSize(val) {
        return ['36', '37', '38', '39', '40', '41'].includes(val);
    }

    function isBagSize(val) {
        return ['xs', 's', 'm', 'l', 'xl', 'xxl'].includes(val);
    }

    function updateTaillesVisibility() {
        if (!selectCategorie) return;

        const selected = normalize(selectCategorie.options[selectCategorie.selectedIndex].text);

        tailleRows.forEach(row => {
            const input = row.querySelector('input');
            if (!input) return;

            const val = normalize(input.value);

            if (selected === 'chaussures' && isShoeSize(val)) {
                row.style.display = '';
            } else if (selected === 'sacs' && isBagSize(val)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    if (selectCategorie) {
        selectCategorie.addEventListener('change', updateTaillesVisibility);
        updateTaillesVisibility();
    }
});

