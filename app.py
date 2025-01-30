import io
import base64
import music21 as m21
from music21 import converter, stream, note, metadata
from dash import Dash, html, dcc, callback, Output, Input, State

# """
app = Dash("Music Generation Project")
app.title = "Music Generation Project"

app.layout = html.Div(
    [
        html.Div(children=
                 [
                    html.H1(children='♪Melody Generator♪', style={'textAlign':'center'}),
                    html.H2(children='"*********** Welcome to the world of Music Generation Project ***********"', style={'textAlign':'center'}),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files', style={'cursor': 'pointer'}),
                        ]),
                        style={
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "margin": "10px",
                        },
                        multiple=False,
                        accept=".mid, .musicxml, .mxl, .krn",

                    ),
                    html.Div(id='output-data-upload'),
                ], style={'margin':'auto'})
    ], style={ 
        'marginTop':'1%',
        'marginBottom':'1%',
        'marginLeft':'20%',
        'marginRight':'20%', 
        'backgroundColor':'#f0f0f0', 
        'padding':'1%'
    }
)

# """
def identify_format_and_load(content):
    try:
        # Try parsing as MusicXML
        return converter.parse(content, format='musicxml')
    except Exception:
        pass
    
    try:
        # Try parsing as MIDI
        return converter.parse(content, format='midi')
    except Exception:
        pass

    try:
        # Try parsing as Kern
        return converter.parse(content, format='humdrum')
    except Exception:
        pass

    raise ValueError("Content could not be parsed into a known format.")


def decode_string(decoded_bytes):
    try:
        return decoded_bytes.decode('utf-8')  # Convert bytes to string
    except Exception:
        pass

    try:
        return decoded_bytes.decode('windows-1252')
    except Exception:
        pass
    try:
        return decoded_bytes.decode('latin-1')
    except Exception:
        pass
    print(str(decoded_bytes))
    return str(decoded_bytes)


def parse_contents(contents, file_extension):
    _, content_string = contents.split(',')
    decoded_str = base64.b64decode(content_string)

    if file_extension == 'krn':
        decoded_str = decode_string(decoded_str)

    score_stream = identify_format_and_load(decoded_str)
    return score_stream

# """
@callback(
        Output('output-data-upload', 'children'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        )
def update_output(contents, filename):
    if contents and filename is not None:
        file_extension = filename.split('.')[-1]
        score_stream = parse_contents(contents, file_extension)

        return f"Successfully uploaded and converted score of file: {filename}"
    return f"File not uploaded yet"



if __name__ == '__main__':
    app.run(debug=True)
    # with open('D:\Python Projects\Melody Generation\Melodies\misc\Bella_ciao.musicxml', 'rb') as file:
    #     song_text = file.read()
    
    # # # decoded_bytes = fun(song_text)
    # score = converter.parse(song_text, format='musicxml')

    # score.show('text')

    # print("check point 1")
