(function() {
  function parseJsonScript(id, fallback) {
    var element = document.getElementById(id);
    if (!element) {
      return fallback;
    }
    try {
      return JSON.parse(element.textContent || '');
    } catch (error) {
      return fallback;
    }
  }

  function createSuggestionButton(item, onSelect) {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'list-group-item list-group-item-action';
    button.textContent = item.label || item.nome || item.modelo || 'Selecionar';
    button.addEventListener('click', function() {
      onSelect(item);
    });
    return button;
  }

  function initTravelerAutocomplete() {
    var wrapper = document.querySelector('.termo-autocomplete[data-type="traveler"]');
    var hiddenInput = document.querySelector('input[name="viajantes_ids"]');
    if (!wrapper || !hiddenInput) {
      return;
    }

    var input = wrapper.querySelector('.termo-autocomplete-input');
    var results = wrapper.querySelector('.termo-autocomplete-results');
    var selectionList = wrapper.querySelector('[data-selection-list]');
    var emptyText = wrapper.querySelector('[data-empty-text]');
    var countBadge = wrapper.querySelector('[data-count-badge]');
    var searchUrl = wrapper.getAttribute('data-search-url') || '';
    var selectedItems = new Map();
    var debounceTimer = null;

    parseJsonScript('termo-selected-viajantes', []).forEach(function(item) {
      if (item && item.id) {
        selectedItems.set(String(item.id), item);
      }
    });

    function syncHiddenInput() {
      hiddenInput.value = Array.from(selectedItems.keys()).join(',');
    }

    function renderSelected() {
      selectionList.innerHTML = '';
      if (!selectedItems.size) {
        emptyText.classList.remove('d-none');
      } else {
        emptyText.classList.add('d-none');
      }
      selectedItems.forEach(function(item, id) {
        var chip = document.createElement('span');
        chip.className = 'termo-selection-chip';

        var label = document.createElement('span');
        label.textContent = item.nome || item.label || 'Servidor';
        chip.appendChild(label);

        var removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'btn btn-sm border-0 bg-transparent text-danger p-0';
        removeButton.innerHTML = '&times;';
        removeButton.addEventListener('click', function() {
          selectedItems.delete(id);
          syncHiddenInput();
          renderSelected();
        });
        chip.appendChild(removeButton);
        selectionList.appendChild(chip);
      });
      if (countBadge) {
        countBadge.textContent = String(selectedItems.size);
      }
    }

    function renderResults(items) {
      if (!results) {
        return;
      }
      results.innerHTML = '';
      if (!items.length) {
        results.classList.add('d-none');
        return;
      }
      items.forEach(function(item) {
        results.appendChild(
          createSuggestionButton(item, function(choice) {
            if (!choice || !choice.id) {
              return;
            }
            selectedItems.set(String(choice.id), choice);
            syncHiddenInput();
            renderSelected();
            input.value = '';
            results.classList.add('d-none');
          })
        );
      });
      results.classList.remove('d-none');
    }

    async function fetchSuggestions(query) {
      if (!query || !searchUrl) {
        renderResults([]);
        return;
      }
      try {
        var response = await fetch(searchUrl + '?q=' + encodeURIComponent(query), {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) {
          return;
        }
        var data = await response.json();
        renderResults(data.results || []);
      } catch (error) {
        renderResults([]);
      }
    }

    if (input) {
      input.addEventListener('input', function() {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(function() {
          fetchSuggestions(input.value.trim());
        }, 180);
      });
      input.addEventListener('blur', function() {
        window.setTimeout(function() {
          results.classList.add('d-none');
        }, 150);
      });
    }

    syncHiddenInput();
    renderSelected();
  }

  function initVehicleAutocomplete() {
    var wrapper = document.querySelector('.termo-autocomplete[data-type="vehicle"]');
    var hiddenInput = document.querySelector('input[name="veiculo_id"]');
    if (!wrapper || !hiddenInput) {
      return;
    }

    var input = wrapper.querySelector('.termo-autocomplete-input');
    var results = wrapper.querySelector('.termo-autocomplete-results');
    var selectionList = wrapper.querySelector('[data-selection-list]');
    var emptyText = wrapper.querySelector('[data-empty-text]');
    var searchUrl = wrapper.getAttribute('data-search-url') || '';
    var selectedItem = parseJsonScript('termo-selected-veiculo', null);
    var debounceTimer = null;

    function syncHiddenInput() {
      hiddenInput.value = selectedItem && selectedItem.id ? String(selectedItem.id) : '';
    }

    function renderSelected() {
      selectionList.innerHTML = '';
      if (!selectedItem || !selectedItem.id) {
        emptyText.classList.remove('d-none');
        return;
      }
      emptyText.classList.add('d-none');
      var chip = document.createElement('div');
      chip.className = 'termo-selection-chip termo-selection-chip--single';
      chip.innerHTML = '<span>' + (selectedItem.label || selectedItem.modelo || 'Viatura') + '</span>';
      var removeButton = document.createElement('button');
      removeButton.type = 'button';
      removeButton.className = 'btn btn-sm border-0 bg-transparent text-danger p-0';
      removeButton.innerHTML = '&times;';
      removeButton.addEventListener('click', function() {
        selectedItem = null;
        syncHiddenInput();
        renderSelected();
      });
      chip.appendChild(removeButton);
      selectionList.appendChild(chip);
    }

    function renderResults(items) {
      if (!results) {
        return;
      }
      results.innerHTML = '';
      if (!items.length) {
        results.classList.add('d-none');
        return;
      }
      items.forEach(function(item) {
        results.appendChild(
          createSuggestionButton(item, function(choice) {
            selectedItem = choice;
            syncHiddenInput();
            renderSelected();
            input.value = '';
            results.classList.add('d-none');
          })
        );
      });
      results.classList.remove('d-none');
    }

    async function fetchSuggestions(query) {
      if (!query || !searchUrl) {
        renderResults([]);
        return;
      }
      try {
        var response = await fetch(searchUrl + '?q=' + encodeURIComponent(query), {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) {
          return;
        }
        var data = await response.json();
        renderResults(data.results || []);
      } catch (error) {
        renderResults([]);
      }
    }

    if (input) {
      input.addEventListener('input', function() {
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(function() {
          fetchSuggestions(input.value.trim());
        }, 180);
      });
      input.addEventListener('blur', function() {
        window.setTimeout(function() {
          results.classList.add('d-none');
        }, 150);
      });
    }

    syncHiddenInput();
    renderSelected();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      initTravelerAutocomplete();
      initVehicleAutocomplete();
    });
  } else {
    initTravelerAutocomplete();
    initVehicleAutocomplete();
  }
})();
