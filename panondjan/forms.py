from django import forms

class DataManageForm(forms.Form):
    trasform_type_ch = [
        ("srt", "sort by value"),
        ("sri", "sort by index"),
        ("ctt", "contact(connect)"),
        ("map", "map"),
        ("aap", "applymap"),
        ("pop", "popout"),
        ("rpc", "replace"),
        ("ist", "insert"),
        ("dpt", "pop duplicated"),
        ("ddp", "drop duplicated"),
        ("pvt", "pivot"),
        ("grp", "group by"),
    ]
    
    data = forms.FileField(
        label='input data' 
    )

    trasform_type = forms.ChoiceField(
        label='trasform way', 
        choices = trasform_type_ch
    )

