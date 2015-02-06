<option value="{{ index }}" {{ 'selected' if selected_preset == index else '' }}
    data-frequency="{{ preset['frequency'] }}"
    data-symbolrate="{{ preset['symbolrate'] }}"
    data-polarization="{{ preset['polarization'] }}"
    data-delivery="{{ preset['delivery'] }}"
    data-modulation="{{ preset['modulation'] }}">{{ pname }}</option>
